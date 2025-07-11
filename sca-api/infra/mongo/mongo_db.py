from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from application.config.dev import MONGO_DB_ENABLE
from infra.exception.exception import CustomException


def mongo_getter(request: Request) -> AsyncIOMotorDatabase:
    """
    获取 mongo 数据库对象

    全局挂载，使用一个数据库对象
    """
    if not MONGO_DB_ENABLE:
        raise CustomException(
            msg="请先开启 MongoDB 数据库连接！",
            desc="请启用 application/settings.py: MONGO_DB_ENABLE"
        )
    return request.app.state.mongo 