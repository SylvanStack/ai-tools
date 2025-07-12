from fastapi import APIRouter, Depends, Body, UploadFile, Request
from redis.asyncio import Redis
from sqlalchemy.orm import joinedload

from apps.user import schemas, models
from apps.user.crud.user_dal import UserDal
from apps.user.params import UserParams
from apps.user.utils.current import AllUserAuth, FullAdminAuth
from apps.user.utils.validation.auth import Auth
from infra.core.dependencies import IdList
from infra.redis.redis_db import redis_getter
from infra.utils.response import SuccessResponse, ErrorResponse

app = APIRouter()

###########################################################
#    用户管理
###########################################################
@app.get("/users", summary="获取用户列表")
async def get_users(
        params: UserParams = Depends(),
        auth: Auth = Depends(FullAdminAuth(permissions=["auth.user.list"]))
):
    model = models.User
    options = [joinedload(model.roles), joinedload(model.depts)]
    schema = schemas.UserOut
    datas, count = await UserDal(auth.db).get_datas(
        **params.dict(),
        v_options=options,
        v_schema=schema,
        v_return_count=True
    )
    return SuccessResponse(datas, count=count)


@app.post("/users", summary="创建用户")
async def create_user(data: schemas.UserIn, auth: Auth = Depends(FullAdminAuth(permissions=["auth.user.create"]))):
    return SuccessResponse(await UserDal(auth.db).create_data(data=data))


@app.delete("/users", summary="批量删除用户", description="软删除，删除后清空所关联的角色")
async def delete_users(ids: IdList = Depends(), auth: Auth = Depends(FullAdminAuth(permissions=["auth.user.delete"]))):
    if auth.user.id in ids.ids:
        return ErrorResponse("不能删除当前登录用户")
    elif 1 in ids.ids:
        return ErrorResponse("不能删除超级管理员用户")
    await UserDal(auth.db).delete_datas(ids=ids.ids, v_soft=True, is_active=False)
    return SuccessResponse("删除成功")


@app.put("/users/{data_id}", summary="更新用户信息")
async def put_user(
        data_id: int,
        data: schemas.UserUpdate,
        auth: Auth = Depends(FullAdminAuth(permissions=["auth.user.update"]))
):
    return SuccessResponse(await UserDal(auth.db).put_data(data_id, data))


@app.get("/users/{data_id}", summary="获取用户信息")
async def get_user(
        data_id: int,
        auth: Auth = Depends(FullAdminAuth(permissions=["auth.user.views", "auth.user.update"]))
):
    model = models.User
    options = [joinedload(model.roles), joinedload(model.depts)]
    schema = schemas.UserOut
    return SuccessResponse(await UserDal(auth.db).get_data(data_id, v_options=options, v_schema=schema))


@app.post("/user/current/reset/password", summary="重置当前用户密码")
async def user_current_reset_password(data: schemas.ResetPwd, auth: Auth = Depends(AllUserAuth())):
    return SuccessResponse(await UserDal(auth.db).reset_current_password(auth.user, data))


@app.post("/user/current/update/info", summary="更新当前用户基本信息")
async def post_user_current_update_info(data: schemas.UserUpdateBaseInfo, auth: Auth = Depends(AllUserAuth())):
    return SuccessResponse(await UserDal(auth.db).update_current_info(auth.user, data))


@app.post("/user/current/update/avatar", summary="更新当前用户头像")
async def post_user_current_update_avatar(file: UploadFile, auth: Auth = Depends(AllUserAuth())):
    return SuccessResponse(await UserDal(auth.db).update_current_avatar(auth.user, file))


@app.get("/user/admin/current/info", summary="获取当前管理员信息")
async def get_user_admin_current_info(auth: Auth = Depends(FullAdminAuth())):
    result = schemas.UserOut.model_validate(auth.user).model_dump()
    result["permissions"] = list(FullAdminAuth.get_user_permissions(auth.user))
    return SuccessResponse(result)


@app.post("/user/export/query/list/to/excel", summary="导出用户查询列表为excel")
async def post_user_export_query_list(
        header: list = Body(..., title="表头与对应字段"),
        params: UserParams = Depends(),
        auth: Auth = Depends(FullAdminAuth(permissions=["auth.user.export"]))
):
    return SuccessResponse(await UserDal(auth.db).export_query_list(header, params))


@app.get("/user/download/import/template", summary="下载最新批量导入用户模板")
async def get_user_download_new_import_template(auth: Auth = Depends(AllUserAuth())):
    return SuccessResponse(await UserDal(auth.db).download_import_template())


@app.post("/import/users", summary="批量导入用户")
async def post_import_users(file: UploadFile, auth: Auth = Depends(FullAdminAuth(permissions=["auth.user.import"]))):
    return SuccessResponse(await UserDal(auth.db).import_users(file))


@app.post("/users/init/password/send/sms", summary="初始化所选用户密码并发送通知短信")
async def post_users_init_password(
        request: Request,
        ids: IdList = Depends(),
        auth: Auth = Depends(FullAdminAuth(permissions=["auth.user.reset"])),
        rd: Redis = Depends(redis_getter)
):
    return SuccessResponse(await UserDal(auth.db).init_password_send_sms(ids.ids, rd))


@app.post("/users/init/password/send/email", summary="初始化所选用户密码并发送通知邮件")
async def post_users_init_password_send_email(
        request: Request,
        ids: IdList = Depends(),
        auth: Auth = Depends(FullAdminAuth(permissions=["auth.user.reset"])),
        rd: Redis = Depends(redis_getter)
):
    return SuccessResponse(await UserDal(auth.db).init_password_send_email(ids.ids, rd))


@app.put("/users/wx/server/openid", summary="更新当前用户服务端微信平台openid")
async def put_user_wx_server_openid(code: str, auth: Auth = Depends(AllUserAuth()), rd: Redis = Depends(redis_getter)):
    result = await UserDal(auth.db).update_wx_server_openid(code, auth.user, rd)
    return SuccessResponse(result)
