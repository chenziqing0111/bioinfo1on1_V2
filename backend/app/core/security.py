from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from cryptography.fernet import Fernet
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database import get_db
from app.models import User


# ========== AES 加密 ==========

class Encryptor:
    """AES-256 加密工具"""

    def __init__(self, key: str):
        # 确保 key 是有效的 Fernet key
        try:
            self.fernet = Fernet(key.encode())
        except Exception:
            # 如果 key 不是有效的 Fernet key，生成一个新的
            self.fernet = Fernet(Fernet.generate_key())

    def encrypt(self, plaintext: str) -> str:
        """加密文本"""
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """解密文本"""
        return self.fernet.decrypt(ciphertext.encode()).decode()


# 初始化加密器
encryptor = Encryptor(settings.AES_ENCRYPTION_KEY)


# ========== JWT 工具 ==========

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """验证 JWT Token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 1002, "message": "无效的 Token"}
        )


# ========== 认证依赖 ==========

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户（依赖注入）"""
    token = credentials.credentials
    payload = verify_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 1002, "message": "无效的 Token"}
        )

    # 从数据库获取用户
    from sqlmodel import select
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 1002, "message": "用户不存在"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 1003, "message": "用户已被禁用"}
        )

    return user


async def get_current_tutor(current_user: User = Depends(get_current_user)) -> User:
    """获取当前导师用户（仅导师可访问）"""
    from app.models import UserRole
    if current_user.role != UserRole.TUTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 1003, "message": "权限不足，仅导师可访问"}
        )
    return current_user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """获取当前管理员用户（仅管理员可访问）"""
    from app.models import UserRole
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 1003, "message": "权限不足，仅管理员可访问"}
        )
    return current_user
