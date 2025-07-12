from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.help import schemas, params, models
from apps.help.crud import IssueCategoryDal
from apps.user.utils.current import AllUserAuth
from apps.user.utils.validation.auth import Auth
from infra.core.dependencies import IdList
from infra.db.database import db_getter
from infra.utils.response import SuccessResponse

app = APIRouter()


###########################################################
#    类别管理
###########################################################
@app.get("/issue/categorys", summary="获取类别列表")
async def get_issue_categorys(p: params.IssueCategoryParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    model = models.IssueCategory
    options = [joinedload(model.create_user)]
    schema = schemas.IssueCategoryListOut
    datas, count = await IssueCategoryDal(auth.db).get_datas(
        **p.dict(),
        v_options=options,
        v_schema=schema,
        v_return_count=True
    )
    return SuccessResponse(datas, count=count)


@app.get("/issue/categorys/options", summary="获取类别选择项")
async def get_issue_categorys_options(auth: Auth = Depends(AllUserAuth())):
    schema = schemas.IssueCategoryOptionsOut
    return SuccessResponse(await IssueCategoryDal(auth.db).get_datas(limit=0, is_active=True, v_schema=schema))


@app.post("/issue/categorys", summary="创建类别")
async def create_issue_category(data: schemas.IssueCategory, auth: Auth = Depends(AllUserAuth())):
    data.create_user_id = auth.user.id
    return SuccessResponse(await IssueCategoryDal(auth.db).create_data(data=data))


@app.delete("/issue/categorys", summary="批量删除类别", description="硬删除")
async def delete_issue_categorys(ids: IdList = Depends(), auth: Auth = Depends(AllUserAuth())):
    await IssueCategoryDal(auth.db).delete_datas(ids=ids.ids, v_soft=False)
    return SuccessResponse("删除成功")


@app.put("/issue/categorys/{data_id}", summary="更新类别信息")
async def put_issue_category(data_id: int, data: schemas.IssueCategory, auth: Auth = Depends(AllUserAuth())):
    return SuccessResponse(await IssueCategoryDal(auth.db).put_data(data_id, data))


@app.get("/issue/categorys/{data_id}", summary="获取类别信息")
async def get_issue_category(data_id: int, auth: Auth = Depends(AllUserAuth())):
    schema = schemas.IssueCategorySimpleOut
    return SuccessResponse(await IssueCategoryDal(auth.db).get_data(data_id, v_schema=schema))


@app.get("/issue/categorys/platform/{platform}", summary="获取平台中的常见问题类别列表")
async def get_issue_category_platform(platform: str, db: AsyncSession = Depends(db_getter)):
    model = models.IssueCategory
    options = [joinedload(model.issues)]
    schema = schemas.IssueCategoryPlatformOut
    result = await IssueCategoryDal(db).get_datas(
        limit=0,
        platform=platform,
        is_active=True,
        v_schema=schema,
        v_options=options
    )
    return SuccessResponse(result)