from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.help import schemas, params, models
from apps.help.crud import IssueDal
from apps.user.utils.current import AllUserAuth
from apps.user.utils.validation.auth import Auth
from infra.core.dependencies import IdList
from infra.db.database import db_getter
from infra.utils.response import SuccessResponse

app = APIRouter()

###########################################################
#    问题管理
###########################################################
@app.get("/issues", summary="获取问题列表")
async def get_issues(p: params.IssueParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    model = models.Issue
    options = [joinedload(model.create_user), joinedload(model.category)]
    schema = schemas.IssueListOut
    datas, count = await IssueDal(auth.db).get_datas(
        **p.dict(),
        v_options=options,
        v_schema=schema,
        v_return_count=True
    )
    return SuccessResponse(datas, count=count)


@app.post("/issues", summary="创建问题")
async def create_issue(data: schemas.Issue, auth: Auth = Depends(AllUserAuth())):
    data.create_user_id = auth.user.id
    return SuccessResponse(await IssueDal(auth.db).create_data(data=data))


@app.delete("/issues", summary="批量删除问题", description="硬删除")
async def delete_issues(ids: IdList = Depends(), auth: Auth = Depends(AllUserAuth())):
    await IssueDal(auth.db).delete_datas(ids=ids.ids, v_soft=False)
    return SuccessResponse("删除成功")


@app.put("/issues/{data_id}", summary="更新问题信息")
async def put_issue(data_id: int, data: schemas.Issue, auth: Auth = Depends(AllUserAuth())):
    return SuccessResponse(await IssueDal(auth.db).put_data(data_id, data))


@app.get("/issues/{data_id}", summary="获取问题信息")
async def get_issue(data_id: int, db: AsyncSession = Depends(db_getter)):
    schema = schemas.IssueSimpleOut
    return SuccessResponse(await IssueDal(db).get_data(data_id, v_schema=schema))


@app.get("/issues/add/view/number/{data_id}", summary="更新常见问题查看次数+1")
async def issue_add_view_number(data_id: int, db: AsyncSession = Depends(db_getter)):
    return SuccessResponse(await IssueDal(db).add_view_number(data_id))
