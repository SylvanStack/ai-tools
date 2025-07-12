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


###########################################################
#    股票基本信息
###########################################################
@app.get("/stock/info", summary="获取股票基本信息列表")
async def get_stock_infos(p: params.StockInfoParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    """
    获取股票基本信息列表
    """
    schema = schemas.StockInfoListOut
    datas, count = await crud.StockInfoDal(auth.db).get_datas(
        **p.dict(),
        v_schema=schema,
        v_return_count=True
    )
    return SuccessResponse(datas, count=count)


@app.get("/stock/info/options", summary="获取股票选择项")
async def get_stock_info_options(auth: Auth = Depends(AllUserAuth())):
    """
    获取股票选择项
    """
    schema = schemas.StockInfoSimpleOut
    return SuccessResponse(await crud.StockInfoDal(auth.db).get_datas(
        limit=0, 
        is_active=True, 
        v_schema=schema
    ))


@app.get("/stock/info/{data_id}", summary="获取股票基本信息详情")
async def get_stock_info(data_id: int, auth: Auth = Depends(AllUserAuth())):
    """
    获取股票基本信息详情
    """
    schema = schemas.StockInfoOut
    return SuccessResponse(await crud.StockInfoDal(auth.db).get_data(data_id, v_schema=schema))


@app.post("/stock/info/sync/{symbol}", summary="同步单个股票基本信息")
async def sync_stock_info(symbol: str, auth: Auth = Depends(AllUserAuth())):
    """
    同步单个股票基本信息
    """
    result = await crud.StockInfoDal(auth.db).sync_stock_info(symbol)
    return SuccessResponse(result)


@app.post("/stock/info/sync/all", summary="同步所有A股股票基本信息")
async def sync_all_stock_info(auth: Auth = Depends(AllUserAuth())):
    """
    同步所有A股股票基本信息
    """
    try:
        result = await crud.StockInfoDal(auth.db).sync_all_stocks()
        return SuccessResponse(result)
    except Exception as e:
        return SuccessResponse({"status": "error", "message": f"股票信息同步失败: {str(e)}"})


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
    datas, count = await crud.StockDailyDal(auth.db).get_datas(
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
    return SuccessResponse(await crud.StockDailyDal(auth.db).get_data(
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
    """
    result = await crud.StockDailyDal(auth.db).sync_stock_daily(
        symbol=symbol, 
        start_date=start_date, 
        end_date=end_date,
        adjust=adjust
    )
    return SuccessResponse(result)


###########################################################
#    股票分钟数据
###########################################################
@app.get("/stock/minute", summary="获取股票分钟数据列表")
async def get_stock_minutes(p: params.StockMinuteParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    """
    获取股票分钟数据列表
    """
    schema = schemas.StockMinuteListOut
    datas, count = await crud.StockMinuteDal(auth.db).get_datas(
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
    return SuccessResponse(await crud.StockMinuteDal(auth.db).get_data(data_id, v_schema=schema))


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
    """
    result = await crud.StockMinuteDal(auth.db).sync_stock_minute(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust
    )
    return SuccessResponse(result) 