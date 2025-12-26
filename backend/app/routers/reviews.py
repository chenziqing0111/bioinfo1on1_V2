from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ReviewCreate, ReviewInfo
from app.core.security import get_current_user
from app.models import User
from app import crud

router = APIRouter()


@router.post("/")
async def create_review(
    request: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """提交评价"""
    # 1. 验证订单存在
    appointment = await crud.get_appointment_by_id(db, request.appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail={"code": 2001, "message": "订单不存在"}
        )

    # 2. 验证是否为订单相关人员
    mentor = await crud.get_mentor_by_user_id(db, current_user.id)
    is_learner = appointment.learner_id == current_user.id
    is_mentor = mentor and appointment.mentor_id == mentor.id

    if not (is_learner or is_mentor):
        raise HTTPException(
            status_code=403,
            detail={"code": 1003, "message": "无权评价此订单"}
        )

    # 3. 创建评价
    review = await crud.create_review(
        db,
        appointment_id=request.appointment_id,
        reviewer_id=current_user.id,
        reviewee_id=request.reviewee_id,
        rating=request.rating,
        content=request.content,
        is_anonymous=request.is_anonymous
    )

    return {"success": True, "data": ReviewInfo.model_validate(review)}


@router.get("/mentor/{mentor_id}")
async def get_mentor_reviews(
    mentor_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """获取导师评价列表"""
    reviews = await crud.get_reviews_for_mentor(db, mentor_id)
    return {
        "success": True,
        "data": {
            "items": [ReviewInfo.model_validate(r) for r in reviews],
            "total": len(reviews)
        }
    }
