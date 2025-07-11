import akshare as ak
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from infra.db.crud import DalBase
from . import models, schemas


class StockMarketDal(DalBase):
    """股票市场总貌数据访问层"""

    def __init__(self, db: AsyncSession):
        super(StockMarketDal, self).__init__()
        self.db = db
        self.model = models.StockMarket
        self.schema = schemas.StockMarketOut

    async def sync_sse_summary(self) -> dict:
        """
        同步上交所市场总貌数据
        """
        try:
            # 获取上交所市场总貌数据
            stock_sse_summary_df = ak.stock_sse_summary()
            # 处理数据并保存
            for _, row in stock_sse_summary_df.iterrows():
                if row['项目'] == '报告时间':
                    date = str(row['股票'])
                    # 检查数据是否已存在
                    exist_data = await self.get_data_by_filter(market="上交所", date=date)
                    if exist_data:
                        continue
                    
                    # 提取数据
                    total_stocks = float(row['股票']) if row['项目'] == '上市股票' else None
                    total_market_value = float(row['股票']) if row['项目'] == '总市值' else None
                    circulating_market_value = float(row['股票']) if row['项目'] == '流通市值' else None
                    total_share_capital = float(row['股票']) if row['项目'] == '总股本' else None
                    circulating_share_capital = float(row['股票']) if row['项目'] == '流通股本' else None
                    average_pe_ratio = float(row['股票']) if row['项目'] == '平均市盈率' else None
                    
                    # 创建数据
                    data = schemas.StockMarket(
                        market="上交所",
                        date=date,
                        total_stocks=total_stocks,
                        total_market_value=total_market_value,
                        circulating_market_value=circulating_market_value,
                        total_share_capital=total_share_capital,
                        circulating_share_capital=circulating_share_capital,
                        average_pe_ratio=average_pe_ratio
                    )
                    await self.create_data(data=data)
            
            return {"status": "success", "message": "上交所市场总貌数据同步成功"}
        except Exception as e:
            return {"status": "error", "message": f"上交所市场总貌数据同步失败: {str(e)}"}

    async def sync_szse_summary(self, date: str) -> dict:
        """
        同步深交所市场总貌数据
        """
        try:
            # 获取深交所市场总貌数据
            stock_szse_summary_df = ak.stock_szse_summary(date=date)
            
            # 检查数据是否已存在
            exist_data = await self.get_data_by_filter(market="深交所", date=date)
            if exist_data:
                return {"status": "info", "message": f"深交所{date}数据已存在"}
            
            # 提取数据
            stock_row = stock_szse_summary_df[stock_szse_summary_df['证券类别'] == '股票'].iloc[0]
            
            # 创建数据
            data = schemas.StockMarket(
                market="深交所",
                date=date,
                total_stocks=int(stock_row['数量']),
                total_market_value=float(stock_row['总市值']),
                circulating_market_value=float(stock_row['流通市值'])
            )
            await self.create_data(data=data)
            
            return {"status": "success", "message": f"深交所{date}市场总貌数据同步成功"}
        except Exception as e:
            return {"status": "error", "message": f"深交所市场总貌数据同步失败: {str(e)}"}


class StockInfoDal(DalBase):
    """股票基本信息数据访问层"""

    def __init__(self, db: AsyncSession):
        super(StockInfoDal, self).__init__()
        self.db = db
        self.model = models.StockInfo
        self.schema = schemas.StockInfoOut

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
        super(StockDailyDal, self).__init__()
        self.db = db
        self.model = models.StockDaily
        self.schema = schemas.StockDailyOut

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
        super(StockMinuteDal, self).__init__()
        self.db = db
        self.model = models.StockMinute
        self.schema = schemas.StockMinuteOut

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
                
                data = schemas.StockMinute(
                    symbol=symbol,
                    trade_time=trade_time,
                    period=period,
                    open_price=float(row['开盘']),
                    close_price=float(row['收盘']),
                    high_price=float(row['最高']),
                    low_price=float(row['最低']),
                    volume=int(row['成交量']),
                    amount=float(row['成交额'])
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