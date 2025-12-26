from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4
from typing import Optional

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DECIMAL, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB


# ========== 枚举定义 ==========

class UserRole(str, Enum):
    STUDENT = "student"
    TUTOR = "tutor"
    ADMIN = "admin"


class AuditStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TagCategory(str, Enum):
    LANGUAGE = "language"
    DOMAIN = "domain"
    TOOL = "tool"


class AppointmentStatus(str, Enum):
    PENDING_ACCEPT = "pending_accept"
    ACCEPTED = "accepted"
    TO_ATTEND = "to_attend"
    IN_PROGRESS = "in_progress"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDING = "refunding"
    REFUNDED = "refunded"


# ========== 数据模型 ==========

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    openid: str = Field(max_length=64, unique=True, index=True)
    role: UserRole = Field(default=UserRole.STUDENT)
    nickname: Optional[str] = Field(default=None, max_length=50)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=100)  # AES 加密存储
    bio: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Mentor(SQLModel, table=True):
    __tablename__ = "mentors"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True)
    title: Optional[str] = Field(default=None, max_length=100)  # 职称
    institution: Optional[str] = Field(default=None, max_length=200)  # 所属机构
    honors: Optional[str] = Field(default=None)  # 荣誉与成就
    resume_json: dict = Field(sa_column=Column(JSONB), default={})
    hourly_rate: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2))
    )
    available_slots: Optional[dict] = Field(sa_column=Column(JSONB), default=None)
    rating: Decimal = Field(
        default=Decimal("5.0"),
        sa_column=Column(DECIMAL(2, 1))
    )
    total_sessions: int = Field(default=0)
    audit_status: AuditStatus = Field(default=AuditStatus.PENDING)
    audit_note: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: int = Field(primary_key=True)
    name: str = Field(max_length=50, unique=True)
    category: TagCategory
    display_order: int = Field(default=0)


class MentorTag(SQLModel, table=True):
    """多对多关联表"""
    __tablename__ = "mentor_tags"

    mentor_id: UUID = Field(foreign_key="mentors.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)


class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_no: str = Field(max_length=32, unique=True, index=True)
    learner_id: UUID = Field(foreign_key="users.id")
    mentor_id: UUID = Field(foreign_key="mentors.id")
    status: AppointmentStatus = Field(default=AppointmentStatus.PENDING_ACCEPT)
    price: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    duration_minutes: int = Field(default=60)
    scheduled_time: Optional[datetime] = Field(default=None)
    meeting_link: Optional[str] = Field(default=None, max_length=500)
    requirements: Optional[str] = Field(default=None)  # AES-256 加密
    accept_nda: bool = Field(default=False)
    nda_signed_at: Optional[datetime] = Field(default=None)
    cancel_reason: Optional[str] = Field(default=None)
    cancelled_by: Optional[UUID] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LessonPlan(SQLModel, table=True):
    __tablename__ = "lesson_plans"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    appointment_id: UUID = Field(foreign_key="appointments.id", unique=True)
    content_md: str  # Markdown 教案内容
    model_name: Optional[str] = Field(default=None, max_length=50)
    input_tokens: Optional[int] = Field(default=None)
    output_tokens: Optional[int] = Field(default=None)
    is_fallback: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint('appointment_id', 'reviewer_id', name='uq_appointment_reviewer'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    appointment_id: UUID = Field(foreign_key="appointments.id")
    reviewer_id: UUID = Field(foreign_key="users.id")
    reviewee_id: UUID = Field(foreign_key="users.id")
    rating: Decimal = Field(sa_column=Column(DECIMAL(2, 1)))  # 1.0-5.0
    content: Optional[str] = Field(default=None)
    is_anonymous: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
