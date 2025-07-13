from fastapi import APIRouter, Depends

from apps.user.utils.current import AllUserAuth
from apps.user.utils.validation.auth import Auth
from infra.utils.response import SuccessResponse
from apps.data_center import schemas, params
from apps.data_center.curd.stock_market_dal import SseMarketDal, SzseMarketDal

app = APIRouter()


###########################################################
#    上海证券交易所市场总貌
###########################################################
@app.get("/stock/market/sse", summary="获取上交所市场总貌数据列表")
async def get_sse_markets(p: params.SseMarketParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    """
    获取上交所市场总貌数据列表
    """
    schema = schemas.SseMarketListOut
    datas, count = await SseMarketDal(auth.db).get_datas(
        **p.dict(),
        v_schema=schema,
        v_return_count=True
    )
    return SuccessResponse(datas, count=count)


@app.get("/stock/market/sse/{data_id}", summary="获取上交所市场总貌详情")
async def get_sse_market(data_id: int, auth: Auth = Depends(AllUserAuth())):
    """
    获取上交所市场总貌详情
    """
    schema = schemas.SseMarketOut
    return SuccessResponse(await SseMarketDal(auth.db).get_data(data_id, v_schema=schema))


@app.post("/stock/market/sse/sync", summary="同步上交所市场总貌数据")
async def sync_sse_market(auth: Auth = Depends(AllUserAuth())):
    """
    同步上交所市场总貌数据
    """
    result = await SseMarketDal(auth.db).sync_sse_summary()
    return SuccessResponse(result)


###########################################################
#    深圳证券交易所市场总貌
###########################################################
@app.get("/stock/market/szse", summary="获取深交所市场总貌数据列表")
async def get_szse_markets(p: params.SzseMarketParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    """
    获取深交所市场总貌数据列表
    """
    schema = schemas.SzseMarketListOut
    datas, count = await SzseMarketDal(auth.db).get_datas(
        **p.dict(),
        v_schema=schema,
        v_return_count=True
    )
    return SuccessResponse(datas, count=count)


@app.get("/stock/market/szse/{data_id}", summary="获取深交所市场总貌详情")
async def get_szse_market(data_id: int, auth: Auth = Depends(AllUserAuth())):
    """
    获取深交所市场总貌详情
    """
    schema = schemas.SzseMarketOut
    return SuccessResponse(await SzseMarketDal(auth.db).get_data(data_id, v_schema=schema))


@app.post("/stock/market/szse/sync", summary="同步深交所市场总貌数据")
async def sync_szse_market(date: str, auth: Auth = Depends(AllUserAuth())):
    """
    同步深交所市场总貌数据
    """
    result = await SzseMarketDal(auth.db).sync_szse_summary(date)
    return SuccessResponse(result)
