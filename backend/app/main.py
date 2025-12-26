from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时清理资源
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": "2.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# 路由注册
from app.routers import auth, mentors, appointments, reviews, ai_engine

app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(mentors.router, prefix="/api/v1/mentors", tags=["导师"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["订单"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["评价"])
app.include_router(ai_engine.router, prefix="/api/v1/ai", tags=["AI"])
