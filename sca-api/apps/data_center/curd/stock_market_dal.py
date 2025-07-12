import akshare as ak
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from infra.db.crud import DalBase
from apps.data_center import models, schemas


class StockMarketDal(DalBase):
    """股票市场总貌数据访问层"""

    def __init__(self, db: AsyncSession):
        super(StockMarketDal, self).__init__(db=db, model=models.StockMarket, schema=schemas.StockMarketOut)

    async def sync_sse_summary(self) -> dict:
        """
        同步上交所市场总貌数据
        """
        try:
            # 获取
            stock_sse_summary_df = ak.stock_sse_summary()
            print("上交所市场总貌数据:")
            print(stock_sse_summary_df)

            # 获取报告时间
            date_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '报告时间'].iloc[0]
            date = str(date_row['股票'])

            # 检查数据是否已存在
            exist_data = await self.get_data_by_filter(market="上交所", date=date)
            if exist_data:
                return {"status": "info", "message": f"上交所{date}数据已存在"}

            # 提取数据
            total_stocks_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '上市股票'].iloc[0]
            total_market_value_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '总市值'].iloc[0]
            circulating_market_value_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '流通市值'].iloc[0]
            total_share_capital_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '总股本'].iloc[0]
            circulating_share_capital_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '流通股本'].iloc[0]
            average_pe_ratio_row = stock_sse_summary_df[stock_sse_summary_df['项目'] == '平均市盈率'].iloc[0]

            # 确保所有数值都被正确转换
            total_stocks = int(float(str(total_stocks_row['股票']).replace(',', ''))) if total_stocks_row[
                '股票'] else None
            total_market_value = float(str(total_market_value_row['股票']).replace(',', '')) if total_market_value_row[
                '股票'] else None
            circulating_market_value = float(str(circulating_market_value_row['股票']).replace(',', '')) if \
            circulating_market_value_row['股票'] else None
            total_share_capital = float(str(total_share_capital_row['股票']).replace(',', '')) if \
            total_share_capital_row['股票'] else None
            circulating_share_capital = float(str(circulating_share_capital_row['股票']).replace(',', '')) if \
            circulating_share_capital_row['股票'] else None
            average_pe_ratio = float(str(average_pe_ratio_row['股票']).replace(',', '')) if average_pe_ratio_row[
                '股票'] else None

            # 创建数据
            data = schemas.StockMarket(
                market="上交所",
                date=date,
                total_stocks=total_stocks,
                total_market_value=total_market_value,
                circulating_market_value=circulating_market_value,
                total_share_capital=total_share_capital,
                circulating_share_capital=circulating_share_capital,
                average_pe_ratio=average_pe_ratio,
                turnover_rate=0.0  # 添加默认值
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
            print("深交所市场总貌数据:")
            print(stock_szse_summary_df)

            # 检查数据是否已存在
            exist_data = await self.get_data_by_filter(market="深交所", date=date)
            if exist_data:
                return {"status": "info", "message": f"深交所{date}数据已存在"}

            # 提取数据
            stock_row = stock_szse_summary_df[stock_szse_summary_df['证券类别'] == '股票'].iloc[0]

            # 安全地转换数值
            def safe_convert(value, convert_func=float):
                if value is None:
                    return None
                if isinstance(value, str):
                    return convert_func(value.replace(',', ''))
                return convert_func(value)

            # 确保所有数值都被正确转换
            total_stocks = safe_convert(stock_row['数量'], int)
            total_market_value = safe_convert(stock_row['总市值'])
            circulating_market_value = safe_convert(stock_row['流通市值'])

            # 创建数据
            data = schemas.StockMarket(
                market="深交所",
                date=date,
                total_stocks=total_stocks,
                total_market_value=total_market_value,
                circulating_market_value=circulating_market_value,
                total_share_capital=0.0,  # 添加默认值
                circulating_share_capital=0.0,  # 添加默认值
                average_pe_ratio=0.0,  # 添加默认值
                turnover_rate=0.0  # 添加默认值
            )
            await self.create_data(data=data)

            return {"status": "success", "message": f"深交所{date}市场总貌数据同步成功"}
        except Exception as e:
            return {"status": "error", "message": f"深交所市场总貌数据同步失败: {str(e)}"}

