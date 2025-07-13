from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.base_model import BaseModel


class SseMarket(BaseModel):
    """上海证券交易所市场总貌表"""
    __tablename__ = "data_sse_market"
    __table_args__ = ({'comment': '上海证券交易所市场总貌表'})

    date: Mapped[str] = mapped_column(String(10), index=True, nullable=False, comment="统计日期")
    total_stocks: Mapped[int] = mapped_column(Integer, comment="上市股票数")
    total_market_value: Mapped[float] = mapped_column(Float, comment="总市值（亿元）")
    circulating_market_value: Mapped[float] = mapped_column(Float, comment="流通市值（亿元）")
    total_share_capital: Mapped[float] = mapped_column(Float, comment="总股本（亿股）")
    circulating_share_capital: Mapped[float] = mapped_column(Float, comment="流通股本（亿股）")
    average_pe_ratio: Mapped[float] = mapped_column(Float, comment="平均市盈率")
    turnover_rate: Mapped[float] = mapped_column(Float, comment="换手率（%）")
    
    # 上交所特有字段
    main_board_stocks: Mapped[int] = mapped_column(Integer, comment="主板股票数")
    sci_tech_board_stocks: Mapped[int] = mapped_column(Integer, comment="科创板股票数")
    main_board_market_value: Mapped[float] = mapped_column(Float, comment="主板市值（亿元）")
    sci_tech_board_market_value: Mapped[float] = mapped_column(Float, comment="科创板市值（亿元）")


class SzseMarket(BaseModel):
    """深圳证券交易所市场总貌表"""
    __tablename__ = "data_szse_market"
    __table_args__ = ({'comment': '深圳证券交易所市场总貌表'})

    date: Mapped[str] = mapped_column(String(10), index=True, nullable=False, comment="统计日期")
    total_stocks: Mapped[int] = mapped_column(Integer, comment="上市股票数")
    total_market_value: Mapped[float] = mapped_column(Float, comment="总市值（亿元）")
    circulating_market_value: Mapped[float] = mapped_column(Float, comment="流通市值（亿元）")
    turnover_rate: Mapped[float] = mapped_column(Float, comment="换手率（%）")
    
    # 深交所特有字段
    main_board_a_stocks: Mapped[int] = mapped_column(Integer, comment="主板A股数量")
    main_board_b_stocks: Mapped[int] = mapped_column(Integer, comment="主板B股数量")
    sme_board_stocks: Mapped[int] = mapped_column(Integer, comment="中小板股票数")
    gem_board_stocks: Mapped[int] = mapped_column(Integer, comment="创业板股票数")
    main_board_a_market_value: Mapped[float] = mapped_column(Float, comment="主板A股市值（亿元）")
    main_board_b_market_value: Mapped[float] = mapped_column(Float, comment="主板B股市值（亿元）")
    sme_board_market_value: Mapped[float] = mapped_column(Float, comment="中小板市值（亿元）")
    gem_board_market_value: Mapped[float] = mapped_column(Float, comment="创业板市值（亿元）")