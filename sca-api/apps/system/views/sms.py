from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from apps.user.curd.user_dal import UserDal
from apps.user.utils.current import OpenAuth
from apps.user.utils.validation.auth import Auth
from infra.redis.redis_db import redis_getter
from infra.utils.response import SuccessResponse, ErrorResponse
from infra.utils.sms.code import CodeSMS

app = APIRouter()


###########################################################
#    短信服务管理
###########################################################
@app.post("/sms/send", summary="发送短信验证码（阿里云服务）")
async def sms_send(telephone: str, rd: Redis = Depends(redis_getter), auth: Auth = Depends(OpenAuth())):
    user = await UserDal(auth.db).get_data(telephone=telephone, v_return_none=True)
    if not user:
        return ErrorResponse("手机号不存在！")
    sms = CodeSMS(telephone, rd)
    return SuccessResponse(await sms.main_async())