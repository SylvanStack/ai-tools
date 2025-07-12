import akshare as ak
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from infra.db.crud import DalBase
from apps.data_center import models, schemas

class StockInfoDal(DalBase):
    """股票基本信息数据访问层"""

    def __init__(self, db: AsyncSession):
        super(StockInfoDal, self).__init__(db=db, model=models.StockInfo, schema=schemas.StockInfoOut)

    async def sync_stock_info(self, symbol: str) -> dict:
        """
        同步单个股票基本信息
        """
        try:
            # 获取股票基本信息
            stock_info_df = ak.stock_individual_info_em(symbol=symbol)
            
            # 检查数据是否已存在
            exist_data = await self.get_data_by_filter(symbol=symbol)
            
            # 提取数据
            info_dict = {row[0]: row[1] for _, row in stock_info_df.iterrows()}
            
            data = schemas.StockInfo(
                symbol=symbol,
                name=info_dict.get('股票简称', ''),
                market="上交所" if symbol.startswith(('60', '68')) else "深交所",
                listing_date=info_dict.get('上市时间', ''),
                total_share_capital=float(info_dict.get('总股本', 0)),
                circulating_share_capital=float(info_dict.get('流通股', 0)),
                is_active=True
            )
            
            if exist_data:
                # 更新数据
                await self.put_data(exist_data.id, data)
                return {"status": "success", "message": f"股票{symbol}信息更新成功"}
            else:
                # 创建数据
                await self.create_data(data=data)
                return {"status": "success", "message": f"股票{symbol}信息同步成功"}
        except Exception as e:
            return {"status": "error", "message": f"股票{symbol}信息同步失败: {str(e)}"}

    async def sync_all_stocks(self) -> dict:
        """
        同步所有A股股票基本信息
        """
        try:
            # 获取所有A股股票列表
            stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
            
            success_count = 0
            error_count = 0
            
            for _, row in stock_zh_a_spot_em_df.iterrows():
                symbol = row['代码']
                try:
                    result = await self.sync_stock_info(symbol)
                    if result['status'] == 'success':
                        success_count += 1
                    else:
                        error_count += 1
                except Exception:
                    error_count += 1
            
            return {
                "status": "success", 
                "message": f"股票信息同步完成，成功: {success_count}，失败: {error_count}"
            }
        except Exception as e:
            return {"status": "error", "message": f"股票信息同步失败: {str(e)}"}


class StockDailyDal(DalBase):
    """股票日线数据访问层"""

    def __init__(self, db: AsyncSession):
        super(StockDailyDal, self).__init__(db=db, model=models.StockDaily, schema=schemas.StockDailyOut)

    async def sync_stock_daily(self, symbol: str, start_date: str, end_date: str, adjust: str = "") -> dict:
        """
        同步股票日线数据
        """
        try:
            # 获取股票日线数据
            stock_zh_a_hist_df = ak.stock_zh_a_hist(
                symbol=symbol, 
                period="daily", 
                start_date=start_date, 
                end_date=end_date,
                adjust=adjust
            )
            
            # 获取股票信息
            stock_info_dal = StockInfoDal(self.db)
            stock_info = await stock_info_dal.get_data_by_filter(symbol=symbol)
            
            if not stock_info:
                # 如果股票信息不存在，先同步股票信息
                await stock_info_dal.sync_stock_info(symbol)
                stock_info = await stock_info_dal.get_data_by_filter(symbol=symbol)
            
            success_count = 0
            update_count = 0
            
            # 处理每一行数据
            for _, row in stock_zh_a_hist_df.iterrows():
                trade_date = row['日期']
                
                # 检查数据是否已存在
                exist_data = await self.get_data_by_filter(symbol=symbol, trade_date=trade_date)
                
                data = schemas.StockDaily(
                    stock_id=stock_info.id,
                    symbol=symbol,
                    trade_date=trade_date,
                    open_price=float(row['开盘']),
                    close_price=float(row['收盘']),
                    high_price=float(row['最高']),
                    low_price=float(row['最低']),
                    volume=int(row['成交量']),
                    amount=float(row['成交额']),
                    amplitude=float(row['振幅']),
                    change_percent=float(row['涨跌幅']),
                    change_amount=float(row['涨跌额']),
                    turnover_rate=float(row['换手率'])
                )
                
                if exist_data:
                    # 更新数据
                    await self.put_data(exist_data.id, data)
                    update_count += 1
                else:
                    # 创建数据
                    await self.create_data(data=data)
                    success_count += 1
            
            return {
                "status": "success", 
                "message": f"股票{symbol}日线数据同步完成，新增: {success_count}，更新: {update_count}"
            }
        except Exception as e:
            return {"status": "error", "message": f"股票{symbol}日线数据同步失败: {str(e)}"}


class StockMinuteDal(DalBase):
    """股票分钟数据访问层"""

    def __init__(self, db: AsyncSession):
        super(StockMinuteDal, self).__init__(db=db, model=models.StockMinute, schema=schemas.StockMinuteOut)

    async def sync_stock_minute(self, symbol: str, period: str, start_date: str = None, end_date: str = None, adjust: str = "") -> dict:
        """
        同步股票分钟数据
        """
        try:
            # 获取股票分钟数据
            stock_zh_a_hist_min_em_df = ak.stock_zh_a_hist_min_em(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            # 检查数据是否为空
            if stock_zh_a_hist_min_em_df is None or stock_zh_a_hist_min_em_df.empty:
                return {
                    "status": "warning", 
                    "message": f"股票{symbol} {period}分钟数据为空，可能是非交易日或数据不可用"
                }
            
            success_count = 0
            update_count = 0
            
            # 处理每一行数据
            for _, row in stock_zh_a_hist_min_em_df.iterrows():
                trade_time = row['时间']
                
                # 检查数据是否已存在
                exist_data = await self.get_data_by_filter(
                    symbol=symbol, 
                    trade_time=trade_time,
                    period=period
                )
                
                # 安全地转换数值
                def safe_convert(value, convert_func=float, default=0):
                    if value is None:
                        return default
                    try:
                        if isinstance(value, str):
                            return convert_func(value.replace(',', ''))
                        return convert_func(value)
                    except (ValueError, TypeError):
                        return default
                
                data = schemas.StockMinute(
                    symbol=symbol,
                    trade_time=trade_time,
                    period=period,
                    open_price=safe_convert(row.get('开盘')),
                    close_price=safe_convert(row.get('收盘')),
                    high_price=safe_convert(row.get('最高')),
                    low_price=safe_convert(row.get('最低')),
                    volume=safe_convert(row.get('成交量'), int),
                    amount=safe_convert(row.get('成交额'))
                )
                
                if exist_data:
                    # 更新数据
                    await self.put_data(exist_data.id, data)
                    update_count += 1
                else:
                    # 创建数据
                    await self.create_data(data=data)
                    success_count += 1
            
            return {
                "status": "success", 
                "message": f"股票{symbol} {period}分钟数据同步完成，新增: {success_count}，更新: {update_count}"
            }
        except Exception as e:
            return {"status": "error", "message": f"股票{symbol} {period}分钟数据同步失败: {str(e)}"} 