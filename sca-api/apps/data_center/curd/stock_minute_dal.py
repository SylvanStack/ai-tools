import logging
import os
import akshare as ak
import pandas as pd
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from apps.data_center import models, schemas
from infra.db.crud import DalBase

# 创建日志记录器
logger = logging.getLogger(__name__)

# 本地数据缓存目录
LOCAL_CACHE_DIR = "apps/data_center/local_data_cache"
STOCK_MINUTE_CACHE_FILE = os.path.join(LOCAL_CACHE_DIR, "stock_minute.csv")


class StockMinuteDal(DalBase):
    """股票分钟数据访问层"""

    def __init__(self, db: AsyncSession):
        super(StockMinuteDal, self).__init__(db=db, model=models.StockMinute, schema=schemas.StockMinuteOut)
        # 确保缓存目录存在
        os.makedirs(LOCAL_CACHE_DIR, exist_ok=True)

    def _get_cached_stock_minute(self, symbol: str, period: str, start_date: str = None, end_date: str = None, adjust: str = "") -> pd.DataFrame:
        """
        从本地缓存获取股票分钟数据
        """
        try:
            if os.path.exists(STOCK_MINUTE_CACHE_FILE):
                # 读取CSV文件
                df = pd.read_csv(STOCK_MINUTE_CACHE_FILE, encoding='utf-8')
                # 过滤指定股票和周期的数据
                stock_df = df[(df['symbol'] == symbol) & (df['period'] == period) & (df['adjust'] == adjust)]
                if not stock_df.empty:
                    # 如果指定了日期范围，则进一步过滤
                    if start_date and end_date:
                        # 提取日期部分用于比较
                        stock_df['date'] = stock_df['trade_time'].str.split(' ').str[0]
                        date_filtered_df = stock_df[(stock_df['date'] >= start_date) & (stock_df['date'] <= end_date)]
                        if not date_filtered_df.empty:
                            logger.info(f"从本地缓存获取股票{symbol} {period}分钟数据成功，日期范围: {start_date}-{end_date}")
                            return date_filtered_df
                    else:
                        # 检查数据是否是今天的
                        today = datetime.now().strftime('%Y-%m-%d')
                        if 'update_date' in stock_df.columns and stock_df.iloc[0]['update_date'] == today:
                            logger.info(f"从本地缓存获取股票{symbol} {period}分钟数据成功")
                            return stock_df
        except Exception as e:
            logger.warning(f"从本地缓存获取股票{symbol} {period}分钟数据失败: {str(e)}")
        return None

    def _save_stock_minute_to_cache(self, symbol: str, period: str, stock_minute_df: pd.DataFrame, adjust: str = "") -> None:
        """
        保存股票分钟数据到本地缓存
        """
        try:
            # 添加股票代码、周期和复权类型列
            stock_minute_df['symbol'] = symbol
            stock_minute_df['period'] = period
            stock_minute_df['adjust'] = adjust
            stock_minute_df['update_date'] = datetime.now().strftime('%Y-%m-%d')
            
            if os.path.exists(STOCK_MINUTE_CACHE_FILE):
                # 读取现有CSV文件
                existing_df = pd.read_csv(STOCK_MINUTE_CACHE_FILE, encoding='utf-8')
                # 删除已有的同一股票同一周期同一复权类型的数据
                existing_df = existing_df[~((existing_df['symbol'] == symbol) & 
                                           (existing_df['period'] == period) & 
                                           (existing_df['adjust'] == adjust))]
                # 合并数据
                updated_df = pd.concat([existing_df, stock_minute_df], ignore_index=True)
                # 保存回CSV
                updated_df.to_csv(STOCK_MINUTE_CACHE_FILE, index=False, encoding='utf-8')
            else:
                # 创建新的CSV文件
                stock_minute_df.to_csv(STOCK_MINUTE_CACHE_FILE, index=False, encoding='utf-8')
            
            logger.info(f"保存股票{symbol} {period}分钟数据到本地缓存成功")
        except Exception as e:
            logger.error(f"保存股票{symbol} {period}分钟数据到本地缓存失败: {str(e)}")

    async def sync_stock_minute(self, symbol: str, period: str, start_date: str = None, end_date: str = None, adjust: str = "") -> dict:
        """
        同步股票分钟数据
        """
        try:
            # 先从本地缓存获取数据
            cached_df = self._get_cached_stock_minute(symbol, period, start_date, end_date, adjust)
            
            # 如果本地缓存没有数据，则从akshare获取
            if cached_df is None:
                # 获取股票分钟数据
                logger.info(f"开始从akshare获取股票{symbol} {period}分钟数据，时间范围: {start_date or '全部'} - {end_date or '全部'}，复权类型: {adjust or '不复权'}")
                stock_zh_a_hist_min_em_df = ak.stock_zh_a_hist_min_em(
                    symbol=symbol,
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    adjust=adjust
                )
                
                # 检查数据是否为空
                if stock_zh_a_hist_min_em_df is None or stock_zh_a_hist_min_em_df.empty:
                    logger.warning(f"股票{symbol} {period}分钟数据为空，可能是非交易日或数据不可用")
                    return {
                        "status": "warning", 
                        "message": f"股票{symbol} {period}分钟数据为空，可能是非交易日或数据不可用"
                    }
                
                logger.info(f"从akshare获取股票{symbol} {period}分钟数据成功，共{len(stock_zh_a_hist_min_em_df)}条记录")
                
                # 保存到本地缓存
                self._save_stock_minute_to_cache(symbol, period, stock_zh_a_hist_min_em_df, adjust)
            else:
                stock_zh_a_hist_min_em_df = cached_df
                logger.info(f"使用本地缓存的股票{symbol} {period}分钟数据，共{len(stock_zh_a_hist_min_em_df)}条记录")
            
            # 将数据写入文件
            with open(f"logs/stock_minute_{symbol}_{period}_{start_date}_{end_date}_{adjust}.txt", "w", encoding="utf-8") as f:
                f.write(f"股票{symbol} {period}分钟数据，时间范围: {start_date or '全部'} - {end_date or '全部'}，复权类型: {adjust or '不复权'}:\n")
                f.write(str(stock_zh_a_hist_min_em_df))
            
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
            for _, row in stock_zh_a_hist_min_em_df.iterrows():
                trade_time = row.get('时间', row.get('trade_time'))
                
                # 检查数据是否已存在
                exist_data = await self.get_data_by_filter(
                    symbol=symbol, 
                    trade_time=trade_time,
                    period=period
                )
                
                # 创建数据对象
                data = schemas.StockMinute(
                    symbol=symbol,
                    trade_time=trade_time,
                    period=period,
                    open_price=safe_convert(row.get('开盘', row.get('open')), float, 0.0),
                    close_price=safe_convert(row.get('收盘', row.get('close')), float, 0.0),
                    high_price=safe_convert(row.get('最高', row.get('high')), float, 0.0),
                    low_price=safe_convert(row.get('最低', row.get('low')), float, 0.0),
                    volume=safe_convert(row.get('成交量', row.get('volume')), int, 0),
                    amount=safe_convert(row.get('成交额', row.get('amount')), float, 0.0),
                    # 新增字段
                    avg_price=safe_convert(row.get('均价', row.get('avg_price')), float, None),
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
            
            logger.info(f"股票{symbol} {period}分钟数据同步完成，新增: {success_count}，更新: {update_count}")
            return {
                "status": "success", 
                "message": f"股票{symbol} {period}分钟数据同步完成，新增: {success_count}，更新: {update_count}"
            }
        except Exception as e:
            logger.error(f"股票{symbol} {period}分钟数据同步失败: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"股票{symbol} {period}分钟数据同步失败: {str(e)}"} 