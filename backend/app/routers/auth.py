from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import WxLoginRequest, WxLoginResponse, UserInfo
from app.core.wechat import wechat_client
from app.core.security import create_access_token, get_current_user
from app.core.config import settings
from app.models import User, UserRole
from app import crud

router = APIRouter()


@router.post("/wx-login", response_model=WxLoginResponse)
async def wx_login(
    request: WxLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """微信登录"""
    # 1. 调用微信 code2Session 接口
    wx_data = await wechat_client.code2session(request.code)

    if "errcode" in wx_data:
        raise HTTPException(
            status_code=401,
            detail={
                "code": 4001,
                "message": f"微信登录失败: {wx_data.get('errmsg', '未知错误')}"
            }
        )

    openid = wx_data["openid"]
    # session_key = wx_data["session_key"]  # 用于解密用户信息，暂不使用

    # 2. 查询或创建用户
    user = await crud.get_user_by_openid(db, openid)
    is_new_user = False

    if not user:
        user = await crud.create_user(db, openid=openid)
        is_new_user = True

    # 3. 生成 JWT Token
    access_token = create_access_token(data={"sub": str(user.id)})

    return WxLoginResponse(
        access_token=access_token,
        token_type="bearer",
        is_new_user=is_new_user
    )


@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    """获取当前用户信息"""
    return {"success": True, "data": UserInfo.model_validate(current_user)}


@router.post("/test-login")
async def test_login(db: AsyncSession = Depends(get_db)):
    """测试登录（仅开发环境）"""
    # 检查是否为开发环境
    if settings.APP_ENV not in ("development", "dev", "local"):
        raise HTTPException(
            status_code=403,
            detail={"code": 4003, "message": "测试登录仅在开发环境可用"}
        )

    # 查找或创建测试用户
    test_openid = "test_user_001"
    user = await crud.get_user_by_openid(db, test_openid)
    is_new_user = False

    if not user:
        user = User(
            openid=test_openid,
            nickname="测试用户",
            role=UserRole.STUDENT
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        is_new_user = True

    # 生成 JWT Token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "is_new_user": is_new_user
        }
    }
