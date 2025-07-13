import logging
import os
import akshare as ak
import pandas as pd
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from apps.data_center import models, schemas
from infra.db.crud import DalBase
from .stock_info_dal import StockInfoDal

# 创建日志记录器
logger = logging.getLogger(__name__)

# 本地数据缓存目录
LOCAL_CACHE_DIR = "apps/data_center/local_data_cache"
STOCK_DAILY_CACHE_FILE = os.path.join(LOCAL_CACHE_DIR, "stock_daily.csv")


class StockDailyDal(DalBase):
    """股票日线数据访问层"""

    def __init__(self, db: AsyncSession):
        super(StockDailyDal, self).__init__(db=db, model=models.StockDaily, schema=schemas.StockDailyOut)
        # 确保缓存目录存在
        os.makedirs(LOCAL_CACHE_DIR, exist_ok=True)

    def _get_cached_stock_daily(self, symbol: str, start_date: str, end_date: str, adjust: str = "") -> pd.DataFrame:
        """
        从本地缓存获取股票日线数据
        """
        try:
            if os.path.exists(STOCK_DAILY_CACHE_FILE):
                # 读取CSV文件
                df = pd.read_csv(STOCK_DAILY_CACHE_FILE, encoding='utf-8')
                # 过滤指定股票的数据
                stock_df = df[(df['symbol'] == symbol) & (df['adjust'] == adjust)]
                if not stock_df.empty:
                    # 过滤日期范围内的数据
                    date_filtered_df = stock_df[(stock_df['trade_date'] >= start_date) & (stock_df['trade_date'] <= end_date)]
                    if not date_filtered_df.empty:
                        # 检查是否包含所有日期范围的数据
                        unique_dates = date_filtered_df['trade_date'].unique()
                        # 如果缓存的数据日期数量与请求的日期范围相符，则使用缓存
                        # 这里简化处理，实际应该计算交易日
                        logger.info(f"从本地缓存获取股票{symbol}日线数据成功，日期范围: {start_date}-{end_date}")
                        return date_filtered_df
        except Exception as e:
            logger.warning(f"从本地缓存获取股票{symbol}日线数据失败: {str(e)}")
        return None

    def _save_stock_daily_to_cache(self, symbol: str, stock_daily_df: pd.DataFrame, adjust: str = "") -> None:
        """
        保存股票日线数据到本地缓存
        """
        try:
            # 添加股票代码和复权类型列
            stock_daily_df['symbol'] = symbol
            stock_daily_df['adjust'] = adjust
            stock_daily_df['update_date'] = datetime.now().strftime('%Y-%m-%d')
            
            if os.path.exists(STOCK_DAILY_CACHE_FILE):
                # 读取现有CSV文件
                existing_df = pd.read_csv(STOCK_DAILY_CACHE_FILE, encoding='utf-8')
                # 删除已有的同一股票同一复权类型的数据
                existing_df = existing_df[~((existing_df['symbol'] == symbol) & (existing_df['adjust'] == adjust))]
                # 合并数据
                updated_df = pd.concat([existing_df, stock_daily_df], ignore_index=True)
                # 保存回CSV
                updated_df.to_csv(STOCK_DAILY_CACHE_FILE, index=False, encoding='utf-8')
            else:
                # 创建新的CSV文件
                stock_daily_df.to_csv(STOCK_DAILY_CACHE_FILE, index=False, encoding='utf-8')
            
            logger.info(f"保存股票{symbol}日线数据到本地缓存成功")
        except Exception as e:
            logger.error(f"保存股票{symbol}日线数据到本地缓存失败: {str(e)}")

    async def sync_stock_daily(self, symbol: str, start_date: str, end_date: str, adjust: str = "") -> dict:
        """
        同步股票日线数据
        """
        try:
            # 先从本地缓存获取数据
            cached_df = self._get_cached_stock_daily(symbol, start_date, end_date, adjust)
            
            # 如果本地缓存没有数据，则从akshare获取
            if cached_df is None:
                # 获取股票日线数据
                logger.info(f"开始从akshare获取股票{symbol}日线数据，时间范围: {start_date} - {end_date}，复权类型: {adjust or '不复权'}")
                stock_zh_a_hist_df = ak.stock_zh_a_hist(
                    symbol=symbol, 
                    period="daily", 
                    start_date=start_date, 
                    end_date=end_date,
                    adjust=adjust
                )
                logger.info(f"从akshare获取股票{symbol}日线数据成功，共{len(stock_zh_a_hist_df)}条记录")
                
                # 保存到本地缓存
                self._save_stock_daily_to_cache(symbol, stock_zh_a_hist_df, adjust)
            else:
                stock_zh_a_hist_df = cached_df
                logger.info(f"使用本地缓存的股票{symbol}日线数据，共{len(stock_zh_a_hist_df)}条记录")
            
            # 将数据写入文件
            with open(f"logs/stock_daily_{symbol}_{start_date}_{end_date}_{adjust}.txt", "w", encoding="utf-8") as f:
                f.write(f"股票{symbol}日线数据，时间范围: {start_date} - {end_date}，复权类型: {adjust or '不复权'}:\n")
                f.write(str(stock_zh_a_hist_df))
            
            # 获取股票信息
            stock_info_dal = StockInfoDal(self.db)
            stock_info = await stock_info_dal.get_data_by_filter(symbol=symbol)
            
            if not stock_info:
                # 如果股票信息不存在，先同步股票信息
                logger.info(f"股票{symbol}信息不存在，开始同步股票信息")
                await stock_info_dal.sync_stock_info(symbol)
                stock_info = await stock_info_dal.get_data_by_filter(symbol=symbol)
                if not stock_info:
                    logger.error(f"同步股票{symbol}信息失败，无法继续同步日线数据")
                    return {"status": "error", "message": f"同步股票{symbol}信息失败，无法继续同步日线数据"}
            
            success_count = 0
            update_count = 0
            
            # 安全地转换数值
            def safe_convert(value, convert_func=float, default=None):
                if value is None or value == '':
                    return default
                try:
                    if isinstance(value, str):
                        return convert_func(value.replace(',', ''))
                    return convert_func(value)
                except (ValueError, TypeError):
                    logger.warning(f"转换值失败: {value}")
                    return default
            
            # 处理每一行数据
            for _, row in stock_zh_a_hist_df.iterrows():
                trade_date = row['日期'] if '日期' in row else row['trade_date']
                
                # 检查数据是否已存在
                exist_data = await self.get_data_by_filter(symbol=symbol, trade_date=trade_date)
                
                data = schemas.StockDaily(
                    stock_id=stock_info.id,
                    symbol=symbol,
                    trade_date=trade_date,
                    open_price=safe_convert(row.get('开盘', row.get('open')), float, 0.0),
                    close_price=safe_convert(row.get('收盘', row.get('close')), float, 0.0),
                    high_price=safe_convert(row.get('最高', row.get('high')), float, 0.0),
                    low_price=safe_convert(row.get('最低', row.get('low')), float, 0.0),
                    volume=safe_convert(row.get('成交量', row.get('volume')), int, 0),
                    amount=safe_convert(row.get('成交额', row.get('amount')), float, 0.0),
                    amplitude=safe_convert(row.get('振幅', row.get('amplitude')), float, 0.0),
                    change_percent=safe_convert(row.get('涨跌幅', row.get('change_percent')), float, 0.0),
                    change_amount=safe_convert(row.get('涨跌额', row.get('change_amount')), float, 0.0),
                    turnover_rate=safe_convert(row.get('换手率', row.get('turnover_rate')), float, 0.0),
                    # 新增字段
                    pre_close=safe_convert(row.get('昨收', row.get('pre_close')), float, None),
                    adjust_flag=adjust
                )
                
                if exist_data:
                    # 更新数据
                    await self.put_data(exist_data.id, data)
                    update_count += 1
                else:
                    # 创建数据
                    await self.create_data(data=data)
                    success_count += 1
            
            logger.info(f"股票{symbol}日线数据同步完成，新增: {success_count}，更新: {update_count}")
            return {
                "status": "success", 
                "message": f"股票{symbol}日线数据同步完成，新增: {success_count}，更新: {update_count}"
            }
        except Exception as e:
            logger.error(f"股票{symbol}日线数据同步失败: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"股票{symbol}日线数据同步失败: {str(e)}"} 