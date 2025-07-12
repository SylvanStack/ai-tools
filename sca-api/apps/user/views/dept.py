from fastapi import APIRouter, Depends

from apps.user import schemas
from apps.user.crud.dept_dal import DeptDal
from apps.user.params import DeptParams
from apps.user.utils.current import FullAdminAuth
from apps.user.utils.validation.auth import Auth
from infra.core.dependencies import IdList
from infra.utils.response import SuccessResponse

app = APIRouter()

###########################################################
#    部门管理
###########################################################
@app.get("/depts", summary="获取部门列表")
async def get_depts(
        params: DeptParams = Depends(),
        auth: Auth = Depends(FullAdminAuth())
):
    datas = await DeptDal(auth.db).get_tree_list(1)
    return SuccessResponse(datas)


@app.get("/dept/tree/options", summary="获取部门树选择项，添加/修改部门时使用")
async def get_dept_options(auth: Auth = Depends(FullAdminAuth())):
    datas = await DeptDal(auth.db).get_tree_list(mode=2)
    return SuccessResponse(datas)


@app.get("/dept/user/tree/options", summary="获取部门树选择项，添加/修改用户时使用")
async def get_dept_treeselect(auth: Auth = Depends(FullAdminAuth())):
    return SuccessResponse(await DeptDal(auth.db).get_tree_list(mode=3))


@app.post("/depts", summary="创建部门信息")
async def create_dept(data: schemas.Dept, auth: Auth = Depends(FullAdminAuth())):
    return SuccessResponse(await DeptDal(auth.db).create_data(data=data))


@app.delete("/depts", summary="批量删除部门", description="硬删除, 如果存在用户关联则无法删除")
async def delete_depts(ids: IdList = Depends(), auth: Auth = Depends(FullAdminAuth())):
    await DeptDal(auth.db).delete_datas(ids.ids, v_soft=False)
    return SuccessResponse("删除成功")


@app.put("/depts/{data_id}", summary="更新部门信息")
async def put_dept(
        data_id: int,
        data: schemas.Dept,
        auth: Auth = Depends(FullAdminAuth())
):
    return SuccessResponse(await DeptDal(auth.db).put_data(data_id, data))