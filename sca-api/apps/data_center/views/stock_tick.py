from fastapi import APIRouter, Depends

from apps.user.utils.current import AllUserAuth
from apps.user.utils.validation.auth import Auth
from infra.utils.response import SuccessResponse
from apps.data_center import schemas, params
from apps.data_center.curd.stock_tick_dal import StockTickDal

app = APIRouter()


###########################################################
#    股票分笔数据
###########################################################
@app.get("/stock/tick", summary="获取股票分笔数据列表")
async def get_stock_ticks(p: params.StockTickParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    """
    获取股票分笔数据列表
    """
    schema = schemas.StockTickListOut
    datas, count = await StockTickDal(auth.db).get_datas(
        **p.dict(),
        v_schema=schema,
        v_return_count=True
    )
    return SuccessResponse(datas, count=count)


@app.get("/stock/tick/{data_id}", summary="获取股票分笔数据详情")
async def get_stock_tick(data_id: int, auth: Auth = Depends(AllUserAuth())):
    """
    获取股票分笔数据详情
    """
    schema = schemas.StockTickOut
    return SuccessResponse(await StockTickDal(auth.db).get_data(data_id, v_schema=schema))


@app.post("/stock/tick/sync", summary="同步股票分笔数据")
async def sync_stock_tick(
    symbol: str, 
    date: str = None, 
    auth: Auth = Depends(AllUserAuth())
):
    """
    同步股票分笔数据
    
    - symbol: 股票代码，如 sh000001 或 sz000001，需要带上市场标识
    - date: 日期，格式 YYYYMMDD，可选，默认为最近交易日
    """
    result = await StockTickDal(auth.db).sync_stock_tick(
        symbol=symbol,
        date=date
    )
    return SuccessResponse(result) 