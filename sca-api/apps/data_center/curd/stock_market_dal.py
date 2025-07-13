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
SSE_MARKET_CACHE_FILE = os.path.join(LOCAL_CACHE_DIR, "sse_market.csv")
SZSE_MARKET_CACHE_FILE = os.path.join(LOCAL_CACHE_DIR, "szse_market.csv")


class SseMarketDal(DalBase):
    """上海证券交易所市场总貌数据访问层"""

    def __init__(self, db: AsyncSession):
        super(SseMarketDal, self).__init__(db=db, model=models.SseMarket, schema=schemas.SseMarketOut)
        # 确保缓存目录存在
        os.makedirs(LOCAL_CACHE_DIR, exist_ok=True)

    def _get_cached_sse_summary(self) -> pd.DataFrame:
        """
        从本地缓存获取上交所市场总貌数据
        """
        try:
            if os.path.exists(SSE_MARKET_CACHE_FILE):
                # 读取CSV文件
                df = pd.read_csv(SSE_MARKET_CACHE_FILE, encoding='utf-8')
                # 检查是否是今天的数据
                today = datetime.now().strftime('%Y-%m-%d')
                if 'update_date' in df.columns and df.iloc[0]['update_date'] == today:
                    logger.info("从本地缓存获取上交所市场总貌数据成功")
                    return df
        except Exception as e:
            logger.warning(f"从本地缓存获取上交所市场总貌数据失败: {str(e)}")
        return None

    def _save_sse_summary_to_cache(self, sse_summary_df: pd.DataFrame) -> None:
        """
        保存上交所市场总貌数据到本地缓存
        """
        try:
            # 添加更新日期列
            sse_summary_df['update_date'] = datetime.now().strftime('%Y-%m-%d')
            # 保存到CSV
            sse_summary_df.to_csv(SSE_MARKET_CACHE_FILE, index=False, encoding='utf-8')
            logger.info("保存上交所市场总貌数据到本地缓存成功")
        except Exception as e:
            logger.error(f"保存上交所市场总貌数据到本地缓存失败: {str(e)}")

    async def sync_sse_summary(self) -> dict:
        """
        同步上交所市场总貌数据
        """
        try:
            # 先从本地缓存获取数据
            cached_df = self._get_cached_sse_summary()
            
            # 如果本地缓存没有数据或者数据不是今天的，则从akshare获取
            if cached_df is None:
                # 获取数据
                logger.info("开始从akshare获取上交所市场总貌数据")
                stock_sse_summary_df = ak.stock_sse_summary()
                logger.info("从akshare获取上交所市场总貌数据成功")
                
                # 保存到本地缓存
                self._save_sse_summary_to_cache(stock_sse_summary_df)
            else:
                stock_sse_summary_df = cached_df
                logger.info("使用本地缓存的上交所市场总貌数据")

            # 获取报告时间
            date_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '报告时间'].iloc[0]
            date = str(date_row['股票'])
            logger.info(f"上交所市场总貌数据日期: {date}")

            # 检查数据是否已存在
            exist_data = await self.get_data_by_filter(date=date)
            if exist_data:
                logger.info(f"上交所{date}数据已存在，无需重复同步")
                return {"status": "info", "message": f"上交所{date}数据已存在"}

            # 提取数据
            total_stocks_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '上市股票'].iloc[0]
            total_market_value_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '总市值'].iloc[0]
            circulating_market_value_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '流通市值'].iloc[0]
            total_share_capital_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '总股本'].iloc[0]
            circulating_share_capital_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '流通股本'].iloc[0]
            average_pe_ratio_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '平均市盈率'].iloc[0]

            # 确保所有数值都被正确转换
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

            total_stocks = safe_convert(total_stocks_row['股票'], int, 0)
            total_market_value = safe_convert(total_market_value_row['股票'], float, 0.0)
            circulating_market_value = safe_convert(circulating_market_value_row['股票'], float, 0.0)
            total_share_capital = safe_convert(total_share_capital_row['股票'], float, 0.0)
            circulating_share_capital = safe_convert(circulating_share_capital_row['股票'], float, 0.0)
            average_pe_ratio = safe_convert(average_pe_ratio_row['股票'], float, 0.0)

            # 获取主板和科创板数据
            main_board_stocks = safe_convert(total_stocks_row['主板'], int, 0)
            sci_tech_board_stocks = safe_convert(total_stocks_row['科创板'], int, 0)
            main_board_market_value = safe_convert(total_market_value_row['主板'], float, 0.0)
            sci_tech_board_market_value = safe_convert(total_market_value_row['科创板'], float, 0.0)

            # 创建数据
            data = schemas.SseMarket(
                date=date,
                total_stocks=total_stocks,
                total_market_value=total_market_value,
                circulating_market_value=circulating_market_value,
                total_share_capital=total_share_capital,
                circulating_share_capital=circulating_share_capital,
                average_pe_ratio=average_pe_ratio,
                turnover_rate=0.0,  # 添加默认值
                main_board_stocks=main_board_stocks,
                sci_tech_board_stocks=sci_tech_board_stocks,
                main_board_market_value=main_board_market_value,
                sci_tech_board_market_value=sci_tech_board_market_value
            )
            
            result = await self.create_data(data=data)
            logger.info(f"上交所{date}市场总貌数据同步成功")
            
            # 将数据写入文件
            with open(f"logs/sse_market_{date}.txt", "w", encoding="utf-8") as f:
                f.write(f"上交所市场总貌数据 {date}:\n")
                f.write(str(stock_sse_summary_df))
                f.write("\n\n处理后的数据:\n")
                f.write(str(data))

            return {"status": "success", "message": f"上交所{date}市场总貌数据同步成功"}
        except Exception as e:
            logger.error(f"上交所市场总貌数据同步失败: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"上交所市场总貌数据同步失败: {str(e)}"}


class SzseMarketDal(DalBase):
    """深圳证券交易所市场总貌数据访问层"""

    def __init__(self, db: AsyncSession):
        super(SzseMarketDal, self).__init__(db=db, model=models.SzseMarket, schema=schemas.SzseMarketOut)
        # 确保缓存目录存在
        os.makedirs(LOCAL_CACHE_DIR, exist_ok=True)

    def _get_cached_szse_summary(self, date: str) -> pd.DataFrame:
        """
        从本地缓存获取深交所市场总貌数据
        """
        try:
            if os.path.exists(SZSE_MARKET_CACHE_FILE):
                # 读取CSV文件
                df = pd.read_csv(SZSE_MARKET_CACHE_FILE, encoding='utf-8')
                # 过滤指定日期的数据
                date_df = df[df['date'] == date]
                if not date_df.empty:
                    logger.info(f"从本地缓存获取深交所{date}市场总貌数据成功")
                    return date_df
        except Exception as e:
            logger.warning(f"从本地缓存获取深交所{date}市场总貌数据失败: {str(e)}")
        return None

    def _save_szse_summary_to_cache(self, date: str, szse_summary_df: pd.DataFrame) -> None:
        """
        保存深交所市场总貌数据到本地缓存
        """
        try:
            # 添加日期和更新日期列
            szse_summary_df['date'] = date
            szse_summary_df['update_date'] = datetime.now().strftime('%Y-%m-%d')
            
            if os.path.exists(SZSE_MARKET_CACHE_FILE):
                # 读取现有CSV文件
                existing_df = pd.read_csv(SZSE_MARKET_CACHE_FILE, encoding='utf-8')
                # 删除已有的同一日期的数据
                existing_df = existing_df[existing_df['date'] != date]
                # 合并数据
                updated_df = pd.concat([existing_df, szse_summary_df], ignore_index=True)
                # 保存回CSV
                updated_df.to_csv(SZSE_MARKET_CACHE_FILE, index=False, encoding='utf-8')
            else:
                # 创建新的CSV文件
                szse_summary_df.to_csv(SZSE_MARKET_CACHE_FILE, index=False, encoding='utf-8')
            
            logger.info(f"保存深交所{date}市场总貌数据到本地缓存成功")
        except Exception as e:
            logger.error(f"保存深交所{date}市场总貌数据到本地缓存失败: {str(e)}")

    async def sync_szse_summary(self, date: str) -> dict:
        """
        同步深交所市场总貌数据
        """
        try:
            # 先从本地缓存获取数据
            cached_df = self._get_cached_szse_summary(date)
            
            # 如果本地缓存没有数据，则从akshare获取
            if cached_df is None:
                # 获取深交所市场总貌数据
                logger.info(f"开始从akshare获取深交所{date}市场总貌数据")
                stock_szse_summary_df = ak.stock_szse_summary(date=date)
                logger.info(f"从akshare获取深交所{date}市场总貌数据成功")
                
                # 保存到本地缓存
                self._save_szse_summary_to_cache(date, stock_szse_summary_df)
            else:
                stock_szse_summary_df = cached_df
                logger.info(f"使用本地缓存的深交所{date}市场总貌数据")

            # 检查数据是否已存在
            exist_data = await self.get_data_by_filter(date=date)
            if exist_data:
                logger.info(f"深交所{date}数据已存在，无需重复同步")
                return {"status": "info", "message": f"深交所{date}数据已存在"}

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

            # 提取数据
            stock_row = stock_szse_summary_df[stock_szse_summary_df['证券类别'] == '股票'].iloc[0] if '股票' in stock_szse_summary_df['证券类别'].values else None
            main_board_a_row = stock_szse_summary_df[stock_szse_summary_df['证券类别'] == '主板A股'].iloc[0] if '主板A股' in stock_szse_summary_df['证券类别'].values else None
            main_board_b_row = stock_szse_summary_df[stock_szse_summary_df['证券类别'] == '主板B股'].iloc[0] if '主板B股' in stock_szse_summary_df['证券类别'].values else None
            sme_board_row = stock_szse_summary_df[stock_szse_summary_df['证券类别'] == '中小板'].iloc[0] if '中小板' in stock_szse_summary_df['证券类别'].values else None
            gem_board_row = stock_szse_summary_df[stock_szse_summary_df['证券类别'] == '创业板A股'].iloc[0] if '创业板A股' in stock_szse_summary_df['证券类别'].values else None

            # 确保所有数值都被正确转换
            total_stocks = safe_convert(stock_row['数量'], int, 0) if stock_row is not None else 0
            total_market_value = safe_convert(stock_row['总市值'], float, 0.0) if stock_row is not None else 0.0
            circulating_market_value = safe_convert(stock_row['流通市值'], float, 0.0) if stock_row is not None else 0.0
            
            # 板块数据
            main_board_a_stocks = safe_convert(main_board_a_row['数量'], int, 0) if main_board_a_row is not None else 0
            main_board_b_stocks = safe_convert(main_board_b_row['数量'], int, 0) if main_board_b_row is not None else 0
            sme_board_stocks = safe_convert(sme_board_row['数量'], int, 0) if sme_board_row is not None else 0
            gem_board_stocks = safe_convert(gem_board_row['数量'], int, 0) if gem_board_row is not None else 0
            
            main_board_a_market_value = safe_convert(main_board_a_row['总市值'], float, 0.0) if main_board_a_row is not None else 0.0
            main_board_b_market_value = safe_convert(main_board_b_row['总市值'], float, 0.0) if main_board_b_row is not None else 0.0
            sme_board_market_value = safe_convert(sme_board_row['总市值'], float, 0.0) if sme_board_row is not None else 0.0
            gem_board_market_value = safe_convert(gem_board_row['总市值'], float, 0.0) if gem_board_row is not None else 0.0

            # 创建数据
            data = schemas.SzseMarket(
                date=date,
                total_stocks=total_stocks,
                total_market_value=total_market_value,
                circulating_market_value=circulating_market_value,
                turnover_rate=0.0,  # 添加默认值
                main_board_a_stocks=main_board_a_stocks,
                main_board_b_stocks=main_board_b_stocks,
                sme_board_stocks=sme_board_stocks,
                gem_board_stocks=gem_board_stocks,
                main_board_a_market_value=main_board_a_market_value,
                main_board_b_market_value=main_board_b_market_value,
                sme_board_market_value=sme_board_market_value,
                gem_board_market_value=gem_board_market_value
            )
            
            result = await self.create_data(data=data)
            logger.info(f"深交所{date}市场总貌数据同步成功")
            
            # 将数据写入文件
            with open(f"logs/szse_market_{date}.txt", "w", encoding="utf-8") as f:
                f.write(f"深交所市场总貌数据 {date}:\n")
                f.write(str(stock_szse_summary_df))
                f.write("\n\n处理后的数据:\n")
                f.write(str(data))

            return {"status": "success", "message": f"深交所{date}市场总貌数据同步成功"}
        except Exception as e:
            logger.error(f"深交所{date}市场总貌数据同步失败: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"深交所市场总貌数据同步失败: {str(e)}"}
