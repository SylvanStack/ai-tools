from sqlalchemy import String, Boolean, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from infra.db.base_model import BaseModel


class StockMarket(BaseModel):
    """股票市场总貌表"""
    __tablename__ = "data_stock_market"
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

class StockInfo(BaseModel):
    """股票基本信息表"""
    __tablename__ = "data_stock_info"
    __table_args__ = ({'comment': '股票基本信息表'})

    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False, comment="股票代码")
    name: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="股票名称")
    market: Mapped[str] = mapped_column(String(20), index=True, nullable=False, comment="市场类型，如上交所、深交所")
    industry: Mapped[str] = mapped_column(String(50), index=True, comment="所属行业")
    listing_date: Mapped[str] = mapped_column(String(10), comment="上市日期")
    total_share_capital: Mapped[float] = mapped_column(Float, comment="总股本（股）")
    circulating_share_capital: Mapped[float] = mapped_column(Float, comment="流通股本（股）")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否有效")
    
    # 与日线数据的关系
    daily_data: Mapped[list["StockDaily"]] = relationship(back_populates="stock_info")
    

class StockDaily(BaseModel):
    """股票日线数据表"""
    __tablename__ = "data_stock_daily"
    __table_args__ = ({'comment': '股票日线数据表'})

    stock_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("data_stock_info.id", ondelete='CASCADE'),
        comment="关联的股票ID"
    )
    stock_info: Mapped["StockInfo"] = relationship(foreign_keys=stock_id, back_populates="daily_data")
    
    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False, comment="股票代码")
    trade_date: Mapped[str] = mapped_column(String(10), index=True, nullable=False, comment="交易日期")
    open_price: Mapped[float] = mapped_column(Float, comment="开盘价")
    close_price: Mapped[float] = mapped_column(Float, comment="收盘价")
    high_price: Mapped[float] = mapped_column(Float, comment="最高价")
    low_price: Mapped[float] = mapped_column(Float, comment="最低价")
    volume: Mapped[int] = mapped_column(Integer, comment="成交量（手）")
    amount: Mapped[float] = mapped_column(Float, comment="成交额（元）")
    amplitude: Mapped[float] = mapped_column(Float, comment="振幅（%）")
    change_percent: Mapped[float] = mapped_column(Float, comment="涨跌幅（%）")
    change_amount: Mapped[float] = mapped_column(Float, comment="涨跌额")
    turnover_rate: Mapped[float] = mapped_column(Float, comment="换手率（%）")
    
class StockMinute(BaseModel):
    """股票分钟数据表"""
    __tablename__ = "data_stock_minute"
    __table_args__ = ({'comment': '股票分钟数据表'})

    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False, comment="股票代码")
    trade_time: Mapped[str] = mapped_column(String(19), index=True, nullable=False, comment="交易时间，格式：YYYY-MM-DD HH:MM:SS")
    period: Mapped[str] = mapped_column(String(10), index=True, nullable=False, comment="周期，如1min、5min、15min、30min、60min")
    open_price: Mapped[float] = mapped_column(Float, comment="开盘价")
    close_price: Mapped[float] = mapped_column(Float, comment="收盘价")
    high_price: Mapped[float] = mapped_column(Float, comment="最高价")
    low_price: Mapped[float] = mapped_column(Float, comment="最低价")
    volume: Mapped[int] = mapped_column(Integer, comment="成交量（手）")
    amount: Mapped[float] = mapped_column(Float, comment="成交额（元）")
