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
STOCK_INFO_CACHE_FILE = os.path.join(LOCAL_CACHE_DIR, "stock_info.csv")


class StockInfoDal(DalBase):
    """股票基本信息数据访问层"""

    def __init__(self, db: AsyncSession):
        super(StockInfoDal, self).__init__(db=db, model=models.StockInfo, schema=schemas.StockInfoOut)
        # 确保缓存目录存在
        os.makedirs(LOCAL_CACHE_DIR, exist_ok=True)

    def _get_cached_stock_info(self, symbol: str) -> pd.DataFrame:
        """
        从本地缓存获取股票信息
        """
        try:
            if os.path.exists(STOCK_INFO_CACHE_FILE):
                # 读取CSV文件
                df = pd.read_csv(STOCK_INFO_CACHE_FILE, encoding='utf-8')
                # 过滤指定股票的数据
                stock_df = df[df['symbol'] == symbol]
                if not stock_df.empty:
                    # 检查数据是否是今天的
                    today = datetime.now().strftime('%Y-%m-%d')
                    if 'update_date' in stock_df.columns and stock_df.iloc[0]['update_date'] == today:
                        logger.info(f"从本地缓存获取股票{symbol}信息成功")
                        return stock_df
        except Exception as e:
            logger.warning(f"从本地缓存获取股票{symbol}信息失败: {str(e)}")
        return None

    def _save_stock_info_to_cache(self, symbol: str, stock_info_df: pd.DataFrame) -> None:
        """
        保存股票信息到本地缓存
        """
        try:
            # 添加更新日期列
            stock_info_df['symbol'] = symbol
            stock_info_df['update_date'] = datetime.now().strftime('%Y-%m-%d')
            
            if os.path.exists(STOCK_INFO_CACHE_FILE):
                # 读取现有CSV文件
                existing_df = pd.read_csv(STOCK_INFO_CACHE_FILE, encoding='utf-8')
                # 删除已有的同一股票数据
                existing_df = existing_df[existing_df['symbol'] != symbol]
                # 合并数据
                updated_df = pd.concat([existing_df, stock_info_df], ignore_index=True)
                # 保存回CSV
                updated_df.to_csv(STOCK_INFO_CACHE_FILE, index=False, encoding='utf-8')
            else:
                # 创建新的CSV文件
                stock_info_df.to_csv(STOCK_INFO_CACHE_FILE, index=False, encoding='utf-8')
            
            logger.info(f"保存股票{symbol}信息到本地缓存成功")
        except Exception as e:
            logger.error(f"保存股票{symbol}信息到本地缓存失败: {str(e)}")

    async def sync_stock_info(self, symbol: str) -> dict:
        """
        同步单个股票基本信息
        """
        try:
            # 特殊处理：如果symbol是"all"，不应该调用stock_individual_info_em
            if symbol.lower() == "all":
                logger.warning("参数symbol='all'不适用于获取单个股票信息，请使用sync_all_stocks方法")
                return {"status": "error", "message": "参数symbol='all'不适用于获取单个股票信息，请使用sync_all_stocks方法"}
            
            # 先从本地缓存获取数据
            cached_df = self._get_cached_stock_info(symbol)
            
            # 如果本地缓存没有数据或者数据不是今天的，则从akshare获取
            if cached_df is None:
                # 获取股票基本信息
                logger.info(f"开始从akshare获取股票{symbol}基本信息")
                stock_info_df = ak.stock_individual_info_em(symbol=symbol)
                logger.info(f"从akshare获取股票{symbol}基本信息成功")
                
                # 保存到本地缓存
                self._save_stock_info_to_cache(symbol, stock_info_df)
            else:
                stock_info_df = cached_df
                logger.info(f"使用本地缓存的股票{symbol}基本信息")
            
            # 检查数据是否已存在
            exist_data = await self.get_data_by_filter(symbol=symbol)
            
            # 提取数据 - 修复FutureWarning，使用iloc替代位置索引
            info_dict = {row.iloc[0]: row.iloc[1] for _, row in stock_info_df.iterrows()}
            
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
            
            # 处理上市时间，确保是字符串类型
            listing_date = info_dict.get('上市时间', '')
            if isinstance(listing_date, int):
                listing_date = str(listing_date)
            
            # 创建数据对象
            data = schemas.StockInfo(
                symbol=symbol,
                name=info_dict.get('股票简称', ''),
                market="上交所" if symbol.startswith(('60', '68')) else "深交所",
                industry=info_dict.get('所属行业', '未知'),  # 添加默认值，避免NULL
                listing_date=listing_date,
                total_share_capital=safe_convert(info_dict.get('总股本', 0)),
                circulating_share_capital=safe_convert(info_dict.get('流通股', 0)),
                is_active=True,
                # 新增字段
                pe_ratio=safe_convert(info_dict.get('市盈率(动)', 0)),
                pb_ratio=safe_convert(info_dict.get('市净率', 0)),
                total_market_value=safe_convert(info_dict.get('总市值', 0)),
                circulating_market_value=safe_convert(info_dict.get('流通市值', 0)),
                chairman=info_dict.get('chairman', ''),
                legal_representative=info_dict.get('legal_representative', ''),
                general_manager=info_dict.get('general_manager', ''),
                secretary=info_dict.get('secretary', ''),
                registered_capital=safe_convert(info_dict.get('reg_asset', 0)),
                established_date=str(info_dict.get('established_date', '')),
                website=info_dict.get('org_website', ''),
                email=info_dict.get('email', ''),
                office_address=info_dict.get('office_address_cn', ''),
                business_scope=info_dict.get('operating_scope', ''),
                company_profile=info_dict.get('org_cn_introduction', '')
            )
            
            # 将数据写入文件
            with open(f"logs/stock_info_{symbol}.txt", "w", encoding="utf-8") as f:
                f.write(f"股票{symbol}基本信息:\n")
                f.write(str(stock_info_df))
                f.write("\n\n处理后的数据:\n")
                f.write(str(data))
            
            if exist_data:
                # 更新数据
                await self.put_data(exist_data.id, data)
                logger.info(f"股票{symbol}信息更新成功")
                return {"status": "success", "message": f"股票{symbol}信息更新成功"}
            else:
                # 创建数据
                await self.create_data(data=data)
                logger.info(f"股票{symbol}信息同步成功")
                return {"status": "success", "message": f"股票{symbol}信息同步成功"}
        except Exception as e:
            logger.error(f"股票{symbol}信息同步失败: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"股票{symbol}信息同步失败: {str(e)}"}

    async def sync_all_stocks(self) -> dict:
        """
        同步所有A股股票基本信息
        """
        try:
            # 获取所有A股股票列表
            logger.info("开始获取所有A股股票列表")
            
            # 检查是否有今天的缓存
            today = datetime.now().strftime('%Y-%m-%d')
            all_stocks_cache_file = os.path.join(LOCAL_CACHE_DIR, f"all_stocks_{today}.csv")
            
            if os.path.exists(all_stocks_cache_file):
                # 从缓存读取
                logger.info("从本地缓存读取A股股票列表")
                stock_zh_a_spot_em_df = pd.read_csv(all_stocks_cache_file, encoding='utf-8')
            else:
                # 从akshare获取
                logger.info("从akshare获取A股股票列表")
                stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
                # 保存到缓存
                stock_zh_a_spot_em_df.to_csv(all_stocks_cache_file, index=False, encoding='utf-8')
                logger.info(f"保存A股股票列表到本地缓存: {all_stocks_cache_file}")
            
            logger.info(f"获取到{len(stock_zh_a_spot_em_df)}只A股股票")
            
            # 确保DataFrame有正确的索引
            if not isinstance(stock_zh_a_spot_em_df.index, pd.RangeIndex):
                stock_zh_a_spot_em_df = stock_zh_a_spot_em_df.reset_index()
            
            # 将数据写入文件
            with open(f"logs/stock_all_list.txt", "w", encoding="utf-8") as f:
                f.write(f"所有A股股票列表:\n")
                f.write(str(stock_zh_a_spot_em_df))
            
            success_count = 0
            error_count = 0
            
            # 确保DataFrame不为空且有正确的索引
            if stock_zh_a_spot_em_df is not None and not stock_zh_a_spot_em_df.empty:
                # 遍历DataFrame的每一行
                for _, row in stock_zh_a_spot_em_df.iterrows():
                    # 确保'代码'列存在
                    if '代码' in row:
                        symbol = row['代码']
                        try:
                            result = await self.sync_stock_info(symbol)
                            if result['status'] == 'success':
                                success_count += 1
                            else:
                                error_count += 1
                        except Exception as e:
                            logger.error(f"同步股票{symbol}信息失败: {str(e)}", exc_info=True)
                            error_count += 1
                    else:
                        logger.warning(f"行数据中没有'代码'列: {row}")
                        error_count += 1
            else:
                logger.error("获取的股票列表为空或无效")
                return {
                    "status": "error", 
                    "message": "获取的股票列表为空或无效"
                }
            
            logger.info(f"股票信息同步完成，成功: {success_count}，失败: {error_count}")
            return {
                "status": "success", 
                "message": f"股票信息同步完成，成功: {success_count}，失败: {error_count}"
            }
        except Exception as e:
            logger.error(f"股票信息同步失败: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"股票信息同步失败: {str(e)}"} 