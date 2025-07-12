from fastapi import APIRouter, Depends, Body

from apps.system import schemas
from apps.system.crud.dict_details_dal import DictDetailsDal
from apps.system.crud.dict_type_dal import DictTypeDal
from apps.system.params import DictTypeParams, DictDetailParams
from apps.user.utils.current import AllUserAuth
from apps.user.utils.validation.auth import Auth
from infra.core.dependencies import IdList
from infra.utils.response import SuccessResponse

app = APIRouter()


###########################################################
#    字典类型管理
###########################################################
@app.get("/dict/types", summary="获取字典类型列表")
async def get_dict_types(p: DictTypeParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    datas, count = await DictTypeDal(auth.db).get_datas(**p.dict(), v_return_count=True)
    return SuccessResponse(datas, count=count)


@app.post("/dict/types", summary="创建字典类型")
async def create_dict_types(data: schemas.DictType, auth: Auth = Depends(AllUserAuth())):
    return SuccessResponse(await DictTypeDal(auth.db).create_data(data=data))


@app.delete("/dict/types", summary="批量删除字典类型")
async def delete_dict_types(ids: IdList = Depends(), auth: Auth = Depends(AllUserAuth())):
    await DictTypeDal(auth.db).delete_datas(ids=ids.ids)
    return SuccessResponse("删除成功")


@app.post("/dict/types/details", summary="获取多个字典类型下的字典元素列表")
async def post_dicts_details(
        auth: Auth = Depends(AllUserAuth()),
        dict_types: list[str] = Body(None, title="字典元素列表", description="查询字典元素列表")
):
    datas = await DictTypeDal(auth.db).get_dicts_details(dict_types)
    return SuccessResponse(datas)


@app.get("/dict/types/options", summary="获取字典类型选择项")
async def get_dicts_options(auth: Auth = Depends(AllUserAuth())):
    return SuccessResponse(await DictTypeDal(auth.db).get_select_datas())


@app.put("/dict/types/{data_id}", summary="更新字典类型")
async def put_dict_types(data_id: int, data: schemas.DictType, auth: Auth = Depends(AllUserAuth())):
    return SuccessResponse(await DictTypeDal(auth.db).put_data(data_id, data))


@app.get("/dict/types/{data_id}", summary="获取字典类型详细")
async def get_dict_type(data_id: int, auth: Auth = Depends(AllUserAuth())):
    schema = schemas.DictTypeSimpleOut
    return SuccessResponse(await DictTypeDal(auth.db).get_data(data_id, v_schema=schema))


###########################################################
#    字典元素管理
###########################################################
@app.post("/dict/details", summary="创建字典元素")
async def create_dict_details(data: schemas.DictDetails, auth: Auth = Depends(AllUserAuth())):
    return SuccessResponse(await DictDetailsDal(auth.db).create_data(data=data))


@app.get("/dict/details", summary="获取单个字典类型下的字典元素列表，分页")
async def get_dict_details(params: DictDetailParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    datas, count = await DictDetailsDal(auth.db).get_datas(**params.dict(), v_return_count=True)
    return SuccessResponse(datas, count=count)


@app.delete("/dict/details", summary="批量删除字典元素", description="硬删除")
async def delete_dict_details(ids: IdList = Depends(), auth: Auth = Depends(AllUserAuth())):
    await DictDetailsDal(auth.db).delete_datas(ids.ids, v_soft=False)
    return SuccessResponse("删除成功")


@app.put("/dict/details/{data_id}", summary="更新字典元素")
async def put_dict_details(data_id: int, data: schemas.DictDetails, auth: Auth = Depends(AllUserAuth())):
    return SuccessResponse(await DictDetailsDal(auth.db).put_data(data_id, data))


@app.get("/dict/details/{data_id}", summary="获取字典元素详情")
async def get_dict_detail(data_id: int, auth: Auth = Depends(AllUserAuth())):
    schema = schemas.DictDetailsSimpleOut
    return SuccessResponse(await DictDetailsDal(auth.db).get_data(data_id, v_schema=schema))