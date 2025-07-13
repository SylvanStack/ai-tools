from fastapi import APIRouter, Depends, Query

from apps.user.utils.current import AllUserAuth
from apps.user.utils.validation.auth import Auth
from infra.utils.response import SuccessResponse
from apps.data_center import schemas, params
from apps.data_center.curd.stock_minute_dal import StockMinuteDal

app = APIRouter()


###########################################################
#    股票分钟数据
###########################################################
@app.get("/stock/minute", summary="获取股票分钟数据列表")
async def get_stock_minutes(p: params.StockMinuteParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    """
    获取股票分钟数据列表
    """
    schema = schemas.StockMinuteListOut
    datas, count = await StockMinuteDal(auth.db).get_datas(
        **p.dict(),
        v_schema=schema,
        v_return_count=True
    )
    return SuccessResponse(datas, count=count)


@app.get("/stock/minute/{data_id}", summary="获取股票分钟数据详情")
async def get_stock_minute(data_id: int, auth: Auth = Depends(AllUserAuth())):
    """
    获取股票分钟数据详情
    """
    schema = schemas.StockMinuteOut
    return SuccessResponse(await StockMinuteDal(auth.db).get_data(data_id, v_schema=schema))


@app.post("/stock/minute/sync", summary="同步股票分钟数据")
async def sync_stock_minute(
    symbol: str, 
    period: str = Query(..., description="周期，如1、5、15、30、60"),
    start_date: str = None, 
    end_date: str = None, 
    adjust: str = "", 
    auth: Auth = Depends(AllUserAuth())
):
    """
    同步股票分钟数据
    
    - symbol: 股票代码，如 000001
    - period: 周期，如1、5、15、30、60
    - start_date: 开始日期，格式 YYYY-MM-DD HH:MM:SS，可选
    - end_date: 结束日期，格式 YYYY-MM-DD HH:MM:SS，可选
    - adjust: 复权类型，可选值：空字符串(不复权)、qfq(前复权)、hfq(后复权)
    """
    result = await StockMinuteDal(auth.db).sync_stock_minute(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust
    )
    return SuccessResponse(result) 