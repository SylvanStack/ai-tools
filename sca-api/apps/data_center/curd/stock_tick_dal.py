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
STOCK_TICK_CACHE_FILE = os.path.join(LOCAL_CACHE_DIR, "stock_tick.csv")


class StockTickDal(DalBase):
    """股票分笔数据访问层"""

    def __init__(self, db: AsyncSession):
        super(StockTickDal, self).__init__(db=db, model=models.StockTick, schema=schemas.StockTickOut)
        # 确保缓存目录存在
        os.makedirs(LOCAL_CACHE_DIR, exist_ok=True)

    def _get_cached_stock_tick(self, symbol: str, date: str = None) -> pd.DataFrame:
        """
        从本地缓存获取股票分笔数据
        """
        try:
            if os.path.exists(STOCK_TICK_CACHE_FILE):
                # 读取CSV文件
                df = pd.read_csv(STOCK_TICK_CACHE_FILE, encoding='utf-8')
                # 过滤指定股票的数据
                stock_df = df[df['symbol'] == symbol]
                if not stock_df.empty:
                    if date:
                        # 提取日期部分用于比较
                        stock_df['date'] = stock_df['trade_time'].str.split(' ').str[0]
                        date_filtered_df = stock_df[stock_df['date'] == date]
                        if not date_filtered_df.empty:
                            logger.info(f"从本地缓存获取股票{symbol}分笔数据成功，日期: {date}")
                            return date_filtered_df
                    else:
                        # 检查数据是否是今天的
                        today = datetime.now().strftime('%Y-%m-%d')
                        if 'update_date' in stock_df.columns and stock_df.iloc[0]['update_date'] == today:
                            logger.info(f"从本地缓存获取股票{symbol}最新分笔数据成功")
                            return stock_df
        except Exception as e:
            logger.warning(f"从本地缓存获取股票{symbol}分笔数据失败: {str(e)}")
        return None

    def _save_stock_tick_to_cache(self, symbol: str, stock_tick_df: pd.DataFrame, date: str = None) -> None:
        """
        保存股票分笔数据到本地缓存
        """
        try:
            # 添加股票代码和日期列
            stock_tick_df['symbol'] = symbol
            stock_tick_df['update_date'] = datetime.now().strftime('%Y-%m-%d')
            
            if os.path.exists(STOCK_TICK_CACHE_FILE):
                # 读取现有CSV文件
                existing_df = pd.read_csv(STOCK_TICK_CACHE_FILE, encoding='utf-8')
                
                # 删除已有的同一股票同一日期的数据
                if date:
                    # 提取日期部分用于比较
                    existing_df['date'] = existing_df['trade_time'].str.split(' ').str[0]
                    existing_df = existing_df[~((existing_df['symbol'] == symbol) & (existing_df['date'] == date))]
                else:
                    # 如果没有指定日期，则删除所有该股票的数据
                    existing_df = existing_df[existing_df['symbol'] != symbol]
                
                # 合并数据
                updated_df = pd.concat([existing_df, stock_tick_df], ignore_index=True)
                # 保存回CSV
                updated_df.to_csv(STOCK_TICK_CACHE_FILE, index=False, encoding='utf-8')
            else:
                # 创建新的CSV文件
                stock_tick_df.to_csv(STOCK_TICK_CACHE_FILE, index=False, encoding='utf-8')
            
            logger.info(f"保存股票{symbol}分笔数据到本地缓存成功")
        except Exception as e:
            logger.error(f"保存股票{symbol}分笔数据到本地缓存失败: {str(e)}")

    async def sync_stock_tick(self, symbol: str, date: str = None) -> dict:
        """
        同步股票分笔数据
        """
        try:
            # 先从本地缓存获取数据
            cached_df = self._get_cached_stock_tick(symbol, date)
            data_source = None
            
            # 如果本地缓存没有数据，则从akshare获取
            if cached_df is None:
                # 获取股票分笔数据
                logger.info(f"开始从akshare获取股票{symbol}分笔数据，日期: {date or '最近交易日'}")
                
                # 根据不同的数据源获取分笔数据
                try:
                    # 先尝试使用腾讯财经的数据源
                    stock_zh_a_tick_tx_js_df = ak.stock_zh_a_tick_tx_js(symbol=symbol)
                    data_source = "腾讯财经"
                    logger.info(f"使用腾讯财经数据源获取股票{symbol}分笔数据成功")
                except Exception as e1:
                    logger.warning(f"使用腾讯财经数据源获取股票{symbol}分笔数据失败: {str(e1)}")
                    try:
                        # 如果腾讯财经失败，尝试使用新浪财经的数据源
                        if date:
                            stock_zh_a_tick_tx_js_df = ak.stock_zh_a_tick_163(symbol=symbol, trade_date=date)
                        else:
                            stock_zh_a_tick_tx_js_df = ak.stock_intraday_sina(symbol=symbol)
                        data_source = "新浪财经"
                        logger.info(f"使用新浪财经数据源获取股票{symbol}分笔数据成功")
                    except Exception as e2:
                        logger.error(f"使用新浪财经数据源获取股票{symbol}分笔数据失败: {str(e2)}")
                        return {
                            "status": "error", 
                            "message": f"获取股票{symbol}分笔数据失败: 腾讯财经和新浪财经数据源均不可用"
                        }
                
                # 检查数据是否为空
                if stock_zh_a_tick_tx_js_df is None or stock_zh_a_tick_tx_js_df.empty:
                    logger.warning(f"股票{symbol}分笔数据为空，可能是非交易日或数据不可用")
                    return {
                        "status": "warning", 
                        "message": f"股票{symbol}分笔数据为空，可能是非交易日或数据不可用"
                    }
                
                logger.info(f"从akshare获取股票{symbol}分笔数据成功，共{len(stock_zh_a_tick_tx_js_df)}条记录")
                
                # 保存到本地缓存
                self._save_stock_tick_to_cache(symbol, stock_zh_a_tick_tx_js_df, date)
            else:
                stock_zh_a_tick_tx_js_df = cached_df
                data_source = "本地缓存"
                logger.info(f"使用本地缓存的股票{symbol}分笔数据，共{len(stock_zh_a_tick_tx_js_df)}条记录")
            
            # 将数据写入文件
            with open(f"logs/stock_tick_{symbol}_{date or 'latest'}.txt", "w", encoding="utf-8") as f:
                f.write(f"股票{symbol}分笔数据，日期: {date or '最近交易日'}，数据源: {data_source}:\n")
                f.write(str(stock_zh_a_tick_tx_js_df))
            
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
            for _, row in stock_zh_a_tick_tx_js_df.iterrows():
                # 根据不同数据源处理字段
                if data_source == "腾讯财经":
                    trade_time = row.get('成交时间', '')
                    price = safe_convert(row.get('成交价格'), float, 0.0)
                    volume = safe_convert(row.get('成交量'), int, 0)
                    amount = safe_convert(row.get('成交额'), float, 0.0)
                    direction = row.get('性质', '')
                    price_change = safe_convert(row.get('价格变动'), float, 0.0)
                elif data_source == "新浪财经":
                    trade_time = row.get('ticktime', '')
                    price = safe_convert(row.get('price'), float, 0.0)
                    volume = safe_convert(row.get('volume'), int, 0)
                    amount = volume * price  # 新浪财经没有成交额，需要自己计算
                    direction = "买盘" if row.get('kind') == 'B' else ("卖盘" if row.get('kind') == 'S' else "中性盘")
                    price_change = safe_convert(row.get('prev_price'), float, 0.0) - price if row.get('prev_price') else None
                else:  # 本地缓存
                    trade_time = row.get('trade_time', '')
                    price = safe_convert(row.get('price'), float, 0.0)
                    volume = safe_convert(row.get('volume'), int, 0)
                    amount = safe_convert(row.get('amount'), float, 0.0)
                    direction = row.get('direction', '')
                    price_change = safe_convert(row.get('price_change'), float, None)
                
                # 检查数据是否已存在
                exist_data = await self.get_data_by_filter(
                    symbol=symbol, 
                    trade_time=trade_time
                )
                
                # 创建数据对象
                data = schemas.StockTick(
                    symbol=symbol,
                    trade_time=trade_time,
                    price=price,
                    volume=volume,
                    amount=amount,
                    direction=direction,
                    price_change=price_change
                )
                
                if exist_data:
                    # 更新数据
                    await self.put_data(exist_data.id, data)
                    update_count += 1
                else:
                    # 创建数据
                    await self.create_data(data=data)
                    success_count += 1
            
            logger.info(f"股票{symbol}分笔数据同步完成，新增: {success_count}，更新: {update_count}")
            return {
                "status": "success", 
                "message": f"股票{symbol}分笔数据同步完成，新增: {success_count}，更新: {update_count}"
            }
        except Exception as e:
            logger.error(f"股票{symbol}分笔数据同步失败: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"股票{symbol}分笔数据同步失败: {str(e)}"} 