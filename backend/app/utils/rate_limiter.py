import redis.asyncio as redis
from functools import wraps
from fastapi import Request, HTTPException
from typing import Callable, Optional

from app.core.config import settings


class RateLimiter:
    """Redis 速率限制器"""

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def check(self, key: str, limit: int, window: int = 60) -> bool:
        """检查是否超过速率限制"""
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, window)
        return current <= limit

    async def close(self):
        """关闭 Redis 连接"""
        await self.redis.close()


# 初始化全局限流器
rate_limiter = RateLimiter(settings.REDIS_URL)


def rate_limit(
    limit: int,
    window: int = 60,
    key_func: Optional[Callable[[Request], str]] = None
):
    """速率限制装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中获取 request 对象
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get('request')

            if not request:
                # 如果没有 request 对象，直接执行
                return await func(*args, **kwargs)

            # 生成限流 key
            if key_func:
                key = key_func(request)
            else:
                key = f"rate:{request.client.host}"

            # 检查限流
            if not await rate_limiter.check(key, limit, window):
                raise HTTPException(
                    status_code=429,
                    detail={"code": 5002, "message": "请求过于频繁，请稍后再试"}
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
