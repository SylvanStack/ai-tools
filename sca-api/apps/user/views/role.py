from fastapi import APIRouter, Depends
from sqlalchemy.orm import joinedload

from apps.user import schemas, models
from apps.user.curd.role_dal import RoleDal
from apps.user.params import RoleParams
from apps.user.utils.current import FullAdminAuth
from apps.user.utils.validation.auth import Auth
from infra.core.dependencies import IdList
from infra.utils.response import SuccessResponse, ErrorResponse

app = APIRouter()

###########################################################
#    角色管理
###########################################################
@app.get("/roles", summary="获取角色列表")
async def get_roles(
        params: RoleParams = Depends(),
        auth: Auth = Depends(FullAdminAuth(permissions=["auth.role.list"]))
):
    datas, count = await RoleDal(auth.db).get_datas(**params.dict(), v_return_count=True)
    return SuccessResponse(datas, count=count)


@app.post("/roles", summary="创建角色信息")
async def create_role(role: schemas.RoleIn, auth: Auth = Depends(FullAdminAuth(permissions=["auth.role.create"]))):
    return SuccessResponse(await RoleDal(auth.db).create_data(data=role))


@app.delete("/roles", summary="批量删除角色", description="硬删除, 如果存在用户关联则无法删除")
async def delete_roles(ids: IdList = Depends(), auth: Auth = Depends(FullAdminAuth(permissions=["auth.role.delete"]))):
    if 1 in ids.ids:
        return ErrorResponse("不能删除管理员角色")
    await RoleDal(auth.db).delete_datas(ids.ids, v_soft=False)
    return SuccessResponse("删除成功")


@app.put("/roles/{data_id}", summary="更新角色信息")
async def put_role(
        data_id: int,
        data: schemas.RoleIn,
        auth: Auth = Depends(FullAdminAuth(permissions=["auth.role.update"]))
):
    if 1 == data_id:
        return ErrorResponse("不能修改管理员角色")
    return SuccessResponse(await RoleDal(auth.db).put_data(data_id, data))


@app.get("/roles/options", summary="获取角色选择项")
async def get_role_options(auth: Auth = Depends(FullAdminAuth(permissions=["auth.user.create", "auth.user.update"]))):
    return SuccessResponse(await RoleDal(auth.db).get_select_datas())


@app.get("/roles/{data_id}", summary="获取角色信息")
async def get_role(
        data_id: int,
        auth: Auth = Depends(FullAdminAuth(permissions=["auth.role.views", "auth.role.update"]))
):
    model = models.Role
    options = [joinedload(model.menus), joinedload(model.depts)]
    schema = schemas.RoleOut
    return SuccessResponse(await RoleDal(auth.db).get_data(data_id, v_options=options, v_schema=schema))
