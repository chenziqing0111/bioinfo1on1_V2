from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import MentorCreate, MentorInfo
from app.core.security import get_current_user, get_current_admin
from app.models import User, AuditStatus, UserRole
from app import crud

router = APIRouter()


@router.get("/")
async def get_mentors(
    db: AsyncSession = Depends(get_db)
):
    """获取导师列表（仅已审核通过）"""
    mentors = await crud.get_approved_mentors(db)
    return {
        "success": True,
        "data": {
            "items": [MentorInfo.model_validate(m) for m in mentors],
            "total": len(mentors)
        }
    }


@router.get("/{mentor_id}")
async def get_mentor_detail(
    mentor_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """获取导师详情"""
    mentor = await crud.get_mentor_by_id(db, mentor_id)
    if not mentor:
        raise HTTPException(
            status_code=404,
            detail={"code": 2004, "message": "导师不存在"}
        )
    return {"success": True, "data": MentorInfo.model_validate(mentor)}


@router.post("/apply")
async def apply_mentor(
    request: MentorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """申请成为导师"""
    # 检查是否已经是导师
    existing = await crud.get_mentor_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail={"code": 2004, "message": "您已经是导师或申请正在审核中"}
        )

    # 创建导师申请
    mentor = await crud.create_mentor(
        db,
        user_id=current_user.id,
        title=request.title,
        institution=request.institution,
        honors=request.honors,
        resume_json=request.resume_json,
        hourly_rate=request.hourly_rate,
        available_slots=request.available_slots
    )

    return {"success": True, "data": MentorInfo.model_validate(mentor)}


@router.put("/{mentor_id}/audit")
async def audit_mentor(
    mentor_id: UUID,
    status: AuditStatus,
    note: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """审核导师（仅管理员）"""
    mentor = await crud.get_mentor_by_id(db, mentor_id)
    if not mentor:
        raise HTTPException(
            status_code=404,
            detail={"code": 2004, "message": "导师不存在"}
        )

    mentor = await crud.update_mentor_audit(db, mentor, status, note)

    # 如果审核通过，更新用户角色为导师
    if status == AuditStatus.APPROVED:
        user = await crud.get_user_by_id(db, mentor.user_id)
        if user:
            await crud.update_user(db, user, role=UserRole.TUTOR)

    return {"success": True, "message": "审核完成", "data": mentor}


@router.get("/tags")
async def get_tags(db: AsyncSession = Depends(get_db)):
    """获取所有标签"""
    tags = await crud.get_all_tags(db)

    # 按类别分组
    result = {
        "language": [],
        "domain": [],
        "tool": []
    }

    for tag in tags:
        result[tag.category.value].append({
            "id": tag.id,
            "name": tag.name
        })

    return {"success": True, "data": result}
