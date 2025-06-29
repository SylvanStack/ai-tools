"""
Mysql 数据库配置项
连接引擎官方文档：https://www.osgeo.cn/sqlalchemy/core/engines.html
数据库链接配置说明：mysql+asyncmy://数据库用户名:数据库密码@数据库地址:数据库端口/数据库名称
"""
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 数据库配置
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "13306")
DB_NAME = os.getenv("DB_NAME", "sca-api")

SQLALCHEMY_DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

"""
Redis 数据库配置
格式："redis://:密码@地址:端口/数据库名称"
"""
REDIS_DB_ENABLE = os.getenv("REDIS_ENABLE", "True") == "True"
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "123456")
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "1")
REDIS_DB_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

"""
MongoDB 数据库配置
格式：mongodb://用户名:密码@地址:端口/?authSource=数据库名称
"""
MONGO_DB_ENABLE = os.getenv("MONGO_ENABLE", "True") == "True"
MONGO_DB_NAME = os.getenv("MONGO_NAME", "sca-api")
MONGO_USER = os.getenv("MONGO_USER", "sca-api")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "123456")
MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource={MONGO_DB_NAME}"

"""
阿里云对象存储OSS配置
阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
 *  [accessKeyId] {String}：通过阿里云控制台创建的AccessKey。
 *  [accessKeySecret] {String}：通过阿里云控制台创建的AccessSecret。
 *  [bucket] {String}：通过控制台或PutBucket创建的bucket。
 *  [endpoint] {String}：bucket所在的区域， 默认oss-cn-hangzhou。
"""
ALIYUN_OSS = {
    "accessKeyId": os.getenv("OSS_ACCESS_KEY_ID", "accessKeyId"),
    "accessKeySecret": os.getenv("OSS_ACCESS_KEY_SECRET", "accessKeySecret"),
    "endpoint": os.getenv("OSS_ENDPOINT", "endpoint"),
    "bucket": os.getenv("OSS_BUCKET", "bucket"),
    "baseUrl": os.getenv("OSS_BASE_URL", "baseUrl")
}

"""
获取IP地址归属地
文档：https://user.ip138.com/ip/doc
"""
IP_PARSE_ENABLE = os.getenv("IP_PARSE_ENABLE", "False") == "True"
IP_PARSE_TOKEN = os.getenv("IP_PARSE_TOKEN", "IP_PARSE_TOKEN")
