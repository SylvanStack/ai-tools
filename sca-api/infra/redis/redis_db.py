from redis.asyncio import Redis
from fastapi import Request
from application.config.dev import REDIS_DB_ENABLE
from infra.exception.exception import CustomException


def redis_getter(request: Request) -> Redis:
    """
    获取 redis 数据库对象

    全局挂载，使用一个数据库对象
    """
    if not REDIS_DB_ENABLE:
        raise CustomException(
            "请先配置Redis数据库链接并启用！",
            desc="请启用 application/settings.py: REDIS_DB_ENABLE"
        )
    return request.app.state.redis 