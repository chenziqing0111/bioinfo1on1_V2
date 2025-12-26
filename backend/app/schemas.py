from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models import UserRole, AuditStatus, AppointmentStatus, TagCategory


# ========== 通用响应 ==========

class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str = "操作成功"


class ErrorResponse(BaseModel):
    success: bool = False
    error: Dict[str, Any]
    data: None = None


# ========== 认证相关 ==========

class WxLoginRequest(BaseModel):
    code: str = Field(..., description="微信登录凭证")


class WxLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool


class UserInfo(BaseModel):
    id: UUID
    openid: str
    role: UserRole
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 导师相关 ==========

class MentorCreate(BaseModel):
    title: str = Field(..., description="职称")
    institution: str = Field(..., description="机构")
    honors: Optional[str] = None
    resume_json: Dict[str, Any] = Field(default={})
    hourly_rate: Decimal = Field(..., description="时薪")
    available_slots: Optional[Dict[str, Any]] = None


class MentorInfo(BaseModel):
    id: UUID
    user_id: UUID
    title: Optional[str]
    institution: Optional[str]
    honors: Optional[str]
    hourly_rate: Decimal
    rating: Decimal
    total_sessions: int
    audit_status: AuditStatus
    created_at: datetime

    class Config:
        from_attributes = True


class MentorListItem(BaseModel):
    id: UUID
    title: Optional[str]
    institution: Optional[str]
    hourly_rate: Decimal
    rating: Decimal
    total_sessions: int
    tags: List[str] = []


# ========== 订单相关 ==========

class AppointmentCreate(BaseModel):
    mentor_id: UUID
    scheduled_time: datetime
    duration_minutes: int = 60
    requirements: str = Field(..., min_length=20, description="需求描述")
    accept_nda: bool = Field(..., description="是否同意保密协议")


class AppointmentInfo(BaseModel):
    id: UUID
    order_no: str
    learner_id: UUID
    mentor_id: UUID
    status: AppointmentStatus
    price: Decimal
    duration_minutes: int
    scheduled_time: Optional[datetime]
    meeting_link: Optional[str]
    accept_nda: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AppointmentAccept(BaseModel):
    meeting_link: Optional[str] = None


class AppointmentCancel(BaseModel):
    reason: str = Field(..., min_length=5, description="取消原因")


# ========== AI 相关 ==========

class MatchRequest(BaseModel):
    requirement: str = Field(..., min_length=20, max_length=2000, description="需求描述")


class MatchRecommendation(BaseModel):
    mentor_id: UUID
    score: float
    reason: str
    can_solve: List[str]


class MatchResponse(BaseModel):
    recommendations: List[MatchRecommendation]


# ========== 评价相关 ==========

class ReviewCreate(BaseModel):
    appointment_id: UUID
    reviewee_id: UUID
    rating: Decimal = Field(..., ge=1.0, le=5.0)
    content: Optional[str] = None
    is_anonymous: bool = False


class ReviewInfo(BaseModel):
    id: UUID
    rating: Decimal
    content: Optional[str]
    is_anonymous: bool
    created_at: datetime

    class Config:
        from_attributes = True
