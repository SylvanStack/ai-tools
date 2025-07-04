"""
Redis 数据库配置

与接口是同一个数据库

格式："redis://:密码@地址:端口/数据库名称"
"""
REDIS_DB_ENABLE = True
REDIS_DB_URL = "redis://:123456@177.8.0.5:6379/1"

"""
MongoDB 数据库配置

与接口是同一个数据库

格式：mongodb://用户名:密码@地址:端口/?authSource=数据库名称
"""
MONGO_DB_ENABLE = True
MONGO_DB_NAME = "sca-api"
MONGO_DB_URL = f"mongodb://sca-api:123456@177.8.0.6:27017/?authSource={MONGO_DB_NAME}"
