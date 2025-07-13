from fastapi import APIRouter, Depends
from sqlalchemy.orm import joinedload

from apps.user.utils.current import AllUserAuth
from apps.user.utils.validation.auth import Auth
from infra.utils.response import SuccessResponse
from apps.data_center import schemas, params, models
from apps.data_center.curd.stock_daily_dal import StockDailyDal

app = APIRouter()


###########################################################
#    股票日线数据
###########################################################
@app.get("/stock/daily", summary="获取股票日线数据列表")
async def get_stock_dailies(p: params.StockDailyParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    """
    获取股票日线数据列表
    """
    model = models.StockDaily
    options = [joinedload(model.stock_info)]
    schema = schemas.StockDailyListOut
    datas, count = await StockDailyDal(auth.db).get_datas(
        **p.dict(),
        v_options=options,
        v_schema=schema,
        v_return_count=True
    )
    return SuccessResponse(datas, count=count)


@app.get("/stock/daily/{data_id}", summary="获取股票日线数据详情")
async def get_stock_daily(data_id: int, auth: Auth = Depends(AllUserAuth())):
    """
    获取股票日线数据详情
    """
    model = models.StockDaily
    options = [joinedload(model.stock_info)]
    schema = schemas.StockDailyListOut
    return SuccessResponse(await StockDailyDal(auth.db).get_data(
        data_id, 
        v_options=options, 
        v_schema=schema
    ))


@app.post("/stock/daily/sync", summary="同步股票日线数据")
async def sync_stock_daily(
    symbol: str, 
    start_date: str, 
    end_date: str, 
    adjust: str = "", 
    auth: Auth = Depends(AllUserAuth())
):
    """
    同步股票日线数据
    
    - symbol: 股票代码，如 000001
    - start_date: 开始日期，格式 YYYYMMDD
    - end_date: 结束日期，格式 YYYYMMDD
    - adjust: 复权类型，可选值：空字符串(不复权)、qfq(前复权)、hfq(后复权)
    """
    result = await StockDailyDal(auth.db).sync_stock_daily(
        symbol=symbol, 
        start_date=start_date, 
        end_date=end_date,
        adjust=adjust
    )
    return SuccessResponse(result) 