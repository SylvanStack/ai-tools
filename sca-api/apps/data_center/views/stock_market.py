from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import joinedload

from apps.user.utils.current import AllUserAuth
from apps.user.utils.validation.auth import Auth
from infra.utils.response import SuccessResponse
from apps.data_center import schemas, params, models
from apps.data_center.curd import crud

app = APIRouter()


###########################################################
#    股票市场总貌
###########################################################
@app.get("/stock/market", summary="获取股票市场总貌数据列表")
async def get_stock_markets(p: params.StockMarketParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    """
    获取股票市场总貌数据列表
    """
    schema = schemas.StockMarketListOut
    datas, count = await crud.StockMarketDal(auth.db).get_datas(
        **p.dict(),
        v_schema=schema,
        v_return_count=True
    )
    return SuccessResponse(datas, count=count)


@app.get("/stock/market/{data_id}", summary="获取股票市场总貌详情")
async def get_stock_market(data_id: int, auth: Auth = Depends(AllUserAuth())):
    """
    获取股票市场总貌详情
    """
    schema = schemas.StockMarketOut
    return SuccessResponse(await crud.StockMarketDal(auth.db).get_data(data_id, v_schema=schema))


@app.post("/stock/market/sync/sse", summary="同步上交所市场总貌数据")
async def sync_sse_market(auth: Auth = Depends(AllUserAuth())):
    """
    同步上交所市场总貌数据
    """
    result = await crud.StockMarketDal(auth.db).sync_sse_summary()
    return SuccessResponse(result)


@app.post("/stock/market/sync/szse", summary="同步深交所市场总貌数据")
async def sync_szse_market(date: str, auth: Auth = Depends(AllUserAuth())):
    """
    同步深交所市场总貌数据
    """
    result = await crud.StockMarketDal(auth.db).sync_szse_summary(date)
    return SuccessResponse(result)

