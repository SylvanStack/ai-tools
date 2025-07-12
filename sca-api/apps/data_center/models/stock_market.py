from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.base_model import BaseModel


class StockMarket(BaseModel):
    """股票市场总貌表"""
    __tablename__ = "stock_market"
    __table_args__ = ({'comment': '股票市场总貌表'})

    market: Mapped[str] = mapped_column(String(20), index=True, nullable=False, comment="市场类型，如上交所、深交所")
    date: Mapped[str] = mapped_column(String(10), index=True, nullable=False, comment="统计日期")
    total_stocks: Mapped[int] = mapped_column(Integer, comment="上市股票数")
    total_market_value: Mapped[float] = mapped_column(Float, comment="总市值（亿元）")
    circulating_market_value: Mapped[float] = mapped_column(Float, comment="流通市值（亿元）")
    total_share_capital: Mapped[float] = mapped_column(Float, comment="总股本（亿股）")
    circulating_share_capital: Mapped[float] = mapped_column(Float, comment="流通股本（亿股）")
    average_pe_ratio: Mapped[float] = mapped_column(Float, comment="平均市盈率")
    turnover_rate: Mapped[float] = mapped_column(Float, comment="换手率（%）")