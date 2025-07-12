from fastapi import APIRouter, Depends

from apps.user.curd.test_dal import TestDal
from apps.user.utils.current import OpenAuth
from apps.user.utils.validation.auth import Auth
from infra.utils.response import SuccessResponse

app = APIRouter()


###########################################################
#    接口测试
###########################################################
@app.get("/test", summary="接口测试")
async def test(auth: Auth = Depends(OpenAuth())):
    return SuccessResponse(await TestDal(auth.db).relationship_where_operations_has())