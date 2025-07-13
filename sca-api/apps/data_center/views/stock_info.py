from fastapi import APIRouter, Depends

from apps.user.utils.current import AllUserAuth
from apps.user.utils.validation.auth import Auth
from infra.utils.response import SuccessResponse
from apps.data_center import schemas, params
from apps.data_center.curd.stock_info_dal import StockInfoDal

app = APIRouter()


###########################################################
#    股票基本信息
###########################################################
@app.get("/stock/info", summary="获取股票基本信息列表")
async def get_stock_infos(p: params.StockInfoParams = Depends(), auth: Auth = Depends(AllUserAuth())):
    """
    获取股票基本信息列表
    """
    schema = schemas.StockInfoListOut
    datas, count = await StockInfoDal(auth.db).get_datas(
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
    return SuccessResponse(await StockInfoDal(auth.db).get_datas(
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
    return SuccessResponse(await StockInfoDal(auth.db).get_data(data_id, v_schema=schema))


@app.post("/stock/info/sync/{symbol}", summary="同步单个股票基本信息")
async def sync_stock_info(symbol: str, auth: Auth = Depends(AllUserAuth())):
    """
    同步单个股票基本信息
    """
    # 如果symbol是"all"，则调用sync_all_stocks方法
    if symbol.lower() == "all":
        try:
            result = await StockInfoDal(auth.db).sync_all_stocks()
            return SuccessResponse(result)
        except Exception as e:
            return SuccessResponse({"status": "error", "message": f"所有股票信息同步失败: {str(e)}"})
    else:
        result = await StockInfoDal(auth.db).sync_stock_info(symbol)
        return SuccessResponse(result)


@app.post("/stock/info/sync/all", summary="同步所有A股股票基本信息")
async def sync_all_stock_info(auth: Auth = Depends(AllUserAuth())):
    """
    同步所有A股股票基本信息
    """
    try:
        result = await StockInfoDal(auth.db).sync_all_stocks()
        return SuccessResponse(result)
    except Exception as e:
        return SuccessResponse({"status": "error", "message": f"股票信息同步失败: {str(e)}"}) 