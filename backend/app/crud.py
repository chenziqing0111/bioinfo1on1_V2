from uuid import UUID
from typing import Optional, List
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_

from app.models import (
    User, Mentor, Tag, MentorTag, Appointment, LessonPlan, Review,
    UserRole, AuditStatus, AppointmentStatus
)


# ========== User CRUD ==========

async def get_user_by_openid(db: AsyncSession, openid: str) -> Optional[User]:
    """根据 openid 获取用户"""
    result = await db.execute(select(User).where(User.openid == openid))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """根据 ID 获取用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    openid: str,
    role: UserRole = UserRole.STUDENT
) -> User:
    """创建用户"""
    user = User(openid=openid, role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, **kwargs) -> User:
    """更新用户信息"""
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


# ========== Mentor CRUD ==========

async def get_mentor_by_id(db: AsyncSession, mentor_id: UUID) -> Optional[Mentor]:
    """根据 ID 获取导师"""
    result = await db.execute(select(Mentor).where(Mentor.id == mentor_id))
    return result.scalar_one_or_none()


async def get_mentor_by_user_id(db: AsyncSession, user_id: UUID) -> Optional[Mentor]:
    """根据用户 ID 获取导师信息"""
    result = await db.execute(select(Mentor).where(Mentor.user_id == user_id))
    return result.scalar_one_or_none()


async def get_approved_mentors(db: AsyncSession) -> List[Mentor]:
    """获取所有已审核通过的导师"""
    result = await db.execute(
        select(Mentor).where(Mentor.audit_status == AuditStatus.APPROVED)
    )
    return result.scalars().all()


async def create_mentor(db: AsyncSession, user_id: UUID, **kwargs) -> Mentor:
    """创建导师"""
    mentor = Mentor(user_id=user_id, **kwargs)
    db.add(mentor)
    await db.commit()
    await db.refresh(mentor)
    return mentor


async def update_mentor_audit(
    db: AsyncSession,
    mentor: Mentor,
    status: AuditStatus,
    note: Optional[str] = None
) -> Mentor:
    """更新导师审核状态"""
    mentor.audit_status = status
    mentor.audit_note = note
    await db.commit()
    await db.refresh(mentor)
    return mentor


# ========== Appointment CRUD ==========

async def get_appointment_by_id(db: AsyncSession, appointment_id: UUID) -> Optional[Appointment]:
    """根据 ID 获取订单"""
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    return result.scalar_one_or_none()


async def get_user_appointments(
    db: AsyncSession,
    user_id: UUID,
    as_learner: bool = True
) -> List[Appointment]:
    """获取用户的订单列表"""
    if as_learner:
        query = select(Appointment).where(Appointment.learner_id == user_id)
    else:
        query = select(Appointment).where(Appointment.mentor_id == user_id)

    result = await db.execute(query.order_by(Appointment.created_at.desc()))
    return result.scalars().all()


async def create_appointment(db: AsyncSession, **kwargs) -> Appointment:
    """创建订单"""
    import time
    import random

    # 生成订单号
    order_no = f"BI{int(time.time())}{random.randint(1000, 9999)}"
    appointment = Appointment(order_no=order_no, **kwargs)
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment


async def update_appointment_status(
    db: AsyncSession,
    appointment: Appointment,
    status: AppointmentStatus
) -> Appointment:
    """更新订单状态"""
    appointment.status = status
    await db.commit()
    await db.refresh(appointment)
    return appointment


# ========== LessonPlan CRUD ==========

async def get_lesson_plan(db: AsyncSession, appointment_id: UUID) -> Optional[LessonPlan]:
    """获取教案"""
    result = await db.execute(
        select(LessonPlan).where(LessonPlan.appointment_id == appointment_id)
    )
    return result.scalar_one_or_none()


async def create_lesson_plan(db: AsyncSession, **kwargs) -> LessonPlan:
    """创建教案"""
    lesson_plan = LessonPlan(**kwargs)
    db.add(lesson_plan)
    await db.commit()
    await db.refresh(lesson_plan)
    return lesson_plan


# ========== Review CRUD ==========

async def get_reviews_for_mentor(db: AsyncSession, mentor_id: UUID) -> List[Review]:
    """获取导师的评价列表"""
    result = await db.execute(
        select(Review).where(Review.reviewee_id == mentor_id).order_by(Review.created_at.desc())
    )
    return result.scalars().all()


async def create_review(db: AsyncSession, **kwargs) -> Review:
    """创建评价"""
    review = Review(**kwargs)
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


# ========== Tag CRUD ==========

async def get_all_tags(db: AsyncSession) -> List[Tag]:
    """获取所有标签"""
    result = await db.execute(select(Tag).order_by(Tag.category, Tag.display_order))
    return result.scalars().all()
