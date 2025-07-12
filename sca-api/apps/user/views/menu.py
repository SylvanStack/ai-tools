from fastapi import APIRouter, Depends

from apps.user import schemas
from apps.user.curd.menu_dal import MenuDal
from apps.user.curd.role_dal import RoleDal
from apps.user.utils.current import FullAdminAuth
from apps.user.utils.validation.auth import Auth
from infra.core.dependencies import IdList
from infra.utils.response import SuccessResponse

app = APIRouter()


###########################################################
#    菜单管理
###########################################################
@app.get("/menus", summary="获取菜单列表")
async def get_menus(auth: Auth = Depends(FullAdminAuth(permissions=["auth.menu.list"]))):
    datas = await MenuDal(auth.db).get_tree_list(mode=1)
    return SuccessResponse(datas)


@app.get("/menus/tree/options", summary="获取菜单树选择项，添加/修改菜单时使用")
async def get_menus_options(auth: Auth = Depends(FullAdminAuth(permissions=["auth.menu.create", "auth.menu.update"]))):
    datas = await MenuDal(auth.db).get_tree_list(mode=2)
    return SuccessResponse(datas)


@app.get("/menus/role/tree/options", summary="获取菜单列表树信息，角色权限使用")
async def get_menus_treeselect(
        auth: Auth = Depends(FullAdminAuth(permissions=["auth.role.create", "auth.role.update"]))
):
    return SuccessResponse(await MenuDal(auth.db).get_tree_list(mode=3))


@app.post("/menus", summary="创建菜单信息")
async def create_menu(menu: schemas.Menu, auth: Auth = Depends(FullAdminAuth(permissions=["auth.menu.create"]))):
    if menu.parent_id:
        menu.alwaysShow = False
    return SuccessResponse(await MenuDal(auth.db).create_data(data=menu))


@app.delete("/menus", summary="批量删除菜单", description="硬删除, 如果存在角色关联则无法删除")
async def delete_menus(ids: IdList = Depends(), auth: Auth = Depends(FullAdminAuth(permissions=["auth.menu.delete"]))):
    await MenuDal(auth.db).delete_datas(ids.ids, v_soft=False)
    return SuccessResponse("删除成功")


@app.put("/menus/{data_id}", summary="更新菜单信息")
async def put_menus(
        data_id: int,
        data: schemas.Menu, auth: Auth = Depends(FullAdminAuth(permissions=["auth.menu.update"]))
):
    return SuccessResponse(await MenuDal(auth.db).put_data(data_id, data))


@app.get("/menus/{data_id}", summary="获取菜单信息")
async def get_menus(
        data_id: int,
        auth: Auth = Depends(FullAdminAuth(permissions=["auth.menu.views", "auth.menu.update"]))
):
    schema = schemas.MenuSimpleOut
    return SuccessResponse(await MenuDal(auth.db).get_data(data_id, v_schema=schema))


@app.get("/role/menus/tree/{role_id}", summary="获取菜单列表树信息以及角色菜单权限ID，角色权限使用")
async def get_role_menu_tree(
        role_id: int,
        auth: Auth = Depends(FullAdminAuth(permissions=["auth.role.create", "auth.role.update"]))
):
    tree_data = await MenuDal(auth.db).get_tree_list(mode=3)
    role_menu_tree = await RoleDal(auth.db).get_role_menu_tree(role_id)
    return SuccessResponse({"role_menu_tree": role_menu_tree, "menus": tree_data})