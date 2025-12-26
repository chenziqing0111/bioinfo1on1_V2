from datetime import datetime
from typing import List
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session_maker
from app.schemas import (
    AppointmentCreate, AppointmentInfo, AppointmentAccept, AppointmentCancel
)
from app.core.security import get_current_user, encryptor
from app.models import User, Appointment, AppointmentStatus
from app import crud
from app.routers.ai_engine import generate_lesson_plan_task

router = APIRouter()


# 状态转换规则
VALID_TRANSITIONS = {
    AppointmentStatus.PENDING_ACCEPT: [
        AppointmentStatus.ACCEPTED,
        AppointmentStatus.CANCELLED
    ],
    AppointmentStatus.ACCEPTED: [
        AppointmentStatus.TO_ATTEND,
        AppointmentStatus.REFUNDING
    ],
    AppointmentStatus.TO_ATTEND: [
        AppointmentStatus.IN_PROGRESS,
        AppointmentStatus.REFUNDING
    ],
    AppointmentStatus.IN_PROGRESS: [
        AppointmentStatus.EVALUATING
    ],
    AppointmentStatus.EVALUATING: [
        AppointmentStatus.COMPLETED
    ],
    AppointmentStatus.REFUNDING: [
        AppointmentStatus.REFUNDED,
        AppointmentStatus.CANCELLED
    ]
}


def validate_transition(from_status: AppointmentStatus, to_status: AppointmentStatus):
    """验证状态转换是否合法"""
    allowed = VALID_TRANSITIONS.get(from_status, [])
    if to_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail={
                "code": 2002,
                "message": f"订单状态不允许从 {from_status.value} 转换到 {to_status.value}"
            }
        )


@router.post("/")
async def create_appointment(
    request: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建订单"""
    # 1. 硬性校验：必须签署 NDA
    if not request.accept_nda:
        raise HTTPException(
            status_code=400,
            detail={"code": 2003, "message": "必须签署保密协议"}
        )

    # 2. 验证导师存在
    mentor = await crud.get_mentor_by_id(db, request.mentor_id)
    if not mentor:
        raise HTTPException(
            status_code=404,
            detail={"code": 2004, "message": "导师不存在"}
        )

    # 3. 不能预约自己
    if mentor.user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail={"code": 2005, "message": "不能预约自己"}
        )

    # 4. 计算价格
    price = (mentor.hourly_rate / 60) * request.duration_minutes

    # 5. 加密需求内容
    encrypted_requirements = encryptor.encrypt(request.requirements)

    # 6. 处理时区问题：去掉时区信息，使用 naive datetime
    if request.scheduled_time.tzinfo:
        scheduled_time = request.scheduled_time.replace(tzinfo=None)
    else:
        scheduled_time = request.scheduled_time
    nda_signed_at = datetime.utcnow()

    # 7. 创建订单
    appointment = await crud.create_appointment(
        db,
        learner_id=current_user.id,
        mentor_id=mentor.id,
        scheduled_time=scheduled_time,
        duration_minutes=request.duration_minutes,
        requirements=encrypted_requirements,
        price=price,
        accept_nda=True,
        nda_signed_at=nda_signed_at
    )

    return {"success": True, "data": AppointmentInfo.model_validate(appointment)}


@router.get("/")
async def get_my_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的订单列表"""
    from app.models import UserRole

    # 根据角色返回不同视角的订单
    if current_user.role == UserRole.TUTOR:
        # 导师查看接单列表
        mentor = await crud.get_mentor_by_user_id(db, current_user.id)
        if mentor:
            appointments = await crud.get_user_appointments(
                db,
                mentor.id,
                as_learner=False
            )
        else:
            appointments = []
    else:
        # 学员查看预约列表
        appointments = await crud.get_user_appointments(
            db,
            current_user.id,
            as_learner=True
        )

    return {
        "success": True,
        "data": {
            "items": [AppointmentInfo.model_validate(a) for a in appointments],
            "total": len(appointments)
        }
    }


@router.get("/{appt_id}")
async def get_appointment_detail(
    appt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取订单详情"""
    appointment = await crud.get_appointment_by_id(db, appt_id)
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail={"code": 2001, "message": "订单不存在"}
        )

    # 验证权限：只能查看自己相关的订单
    mentor = await crud.get_mentor_by_user_id(db, current_user.id)
    is_learner = appointment.learner_id == current_user.id
    is_mentor = mentor and appointment.mentor_id == mentor.id

    if not (is_learner or is_mentor):
        raise HTTPException(
            status_code=403,
            detail={"code": 1003, "message": "无权查看此订单"}
        )

    return {"success": True, "data": AppointmentInfo.model_validate(appointment)}


@router.post("/{appt_id}/accept")
async def accept_appointment(
    appt_id: UUID,
    request: AppointmentAccept,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导师接单"""
    from app.models import UserRole

    # 1. 验证当前用户是导师
    if current_user.role != UserRole.TUTOR:
        raise HTTPException(
            status_code=403,
            detail={"code": 1003, "message": "仅导师可接单"}
        )

    # 2. 获取订单
    appointment = await crud.get_appointment_by_id(db, appt_id)
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail={"code": 2001, "message": "订单不存在"}
        )

    # 3. 验证是否为该订单的导师
    mentor = await crud.get_mentor_by_user_id(db, current_user.id)
    if not mentor or appointment.mentor_id != mentor.id:
        raise HTTPException(
            status_code=403,
            detail={"code": 1003, "message": "无权接此订单"}
        )

    # 4. 验证状态转换
    validate_transition(appointment.status, AppointmentStatus.ACCEPTED)

    # 5. 更新状态
    appointment.status = AppointmentStatus.ACCEPTED
    if request.meeting_link:
        appointment.meeting_link = request.meeting_link
        appointment.status = AppointmentStatus.TO_ATTEND

    await db.commit()
    await db.refresh(appointment)

    # 6. 异步生成 AI 教案
    decrypted_requirements = encryptor.decrypt(appointment.requirements)
    background_tasks.add_task(
        generate_lesson_plan_task,
        appointment.id,
        decrypted_requirements,
        async_session_maker
    )

    return {"success": True, "message": "接单成功", "data": appointment}


@router.post("/{appt_id}/cancel")
async def cancel_appointment(
    appt_id: UUID,
    request: AppointmentCancel,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消订单"""
    # 1. 获取订单
    appointment = await crud.get_appointment_by_id(db, appt_id)
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail={"code": 2001, "message": "订单不存在"}
        )

    # 2. 验证权限
    mentor = await crud.get_mentor_by_user_id(db, current_user.id)
    is_learner = appointment.learner_id == current_user.id
    is_mentor = mentor and appointment.mentor_id == mentor.id

    if not (is_learner or is_mentor):
        raise HTTPException(
            status_code=403,
            detail={"code": 1003, "message": "无权取消此订单"}
        )

    # 3. 验证状态
    if appointment.status not in [
        AppointmentStatus.PENDING_ACCEPT,
        AppointmentStatus.ACCEPTED
    ]:
        raise HTTPException(
            status_code=400,
            detail={"code": 2002, "message": "当前状态不允许取消"}
        )

    # 4. 更新状态
    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancel_reason = request.reason
    appointment.cancelled_by = current_user.id

    await db.commit()

    return {"success": True, "message": "订单已取消"}


@router.get("/{appt_id}/lesson-plan")
async def get_lesson_plan(
    appt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 AI 教案"""
    # 1. 获取订单
    appointment = await crud.get_appointment_by_id(db, appt_id)
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail={"code": 2001, "message": "订单不存在"}
        )

    # 2. 验证权限
    mentor = await crud.get_mentor_by_user_id(db, current_user.id)
    is_learner = appointment.learner_id == current_user.id
    is_mentor = mentor and appointment.mentor_id == mentor.id

    if not (is_learner or is_mentor):
        raise HTTPException(
            status_code=403,
            detail={"code": 1003, "message": "无权查看教案"}
        )

    # 3. 获取教案
    lesson_plan = await crud.get_lesson_plan(db, appt_id)
    if not lesson_plan:
        return {
            "success": True,
            "data": None,
            "message": "教案正在生成中，请稍后刷新"
        }

    return {
        "success": True,
        "data": {
            "content_md": lesson_plan.content_md,
            "model_name": lesson_plan.model_name,
            "is_fallback": lesson_plan.is_fallback,
            "created_at": lesson_plan.created_at
        }
    }
