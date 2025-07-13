from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from infra.db.base_model import BaseModel

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
    
    # 新增字段
    pe_ratio: Mapped[float] = mapped_column(Float, nullable=True, comment="市盈率")
    pb_ratio: Mapped[float] = mapped_column(Float, nullable=True, comment="市净率")
    total_market_value: Mapped[float] = mapped_column(Float, nullable=True, comment="总市值（元）")
    circulating_market_value: Mapped[float] = mapped_column(Float, nullable=True, comment="流通市值（元）")
    chairman: Mapped[str] = mapped_column(String(50), nullable=True, comment="董事长")
    legal_representative: Mapped[str] = mapped_column(String(50), nullable=True, comment="法定代表人")
    general_manager: Mapped[str] = mapped_column(String(50), nullable=True, comment="总经理")
    secretary: Mapped[str] = mapped_column(String(50), nullable=True, comment="董秘")
    registered_capital: Mapped[float] = mapped_column(Float, nullable=True, comment="注册资本")
    established_date: Mapped[str] = mapped_column(String(10), nullable=True, comment="成立日期")
    website: Mapped[str] = mapped_column(String(100), nullable=True, comment="公司网站")
    email: Mapped[str] = mapped_column(String(100), nullable=True, comment="公司邮箱")
    office_address: Mapped[str] = mapped_column(String(200), nullable=True, comment="办公地址")
    business_scope: Mapped[str] = mapped_column(String(1000), nullable=True, comment="经营范围")
    company_profile: Mapped[str] = mapped_column(String(2000), nullable=True, comment="公司简介")
    
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
    
    # 新增字段
    pre_close: Mapped[float] = mapped_column(Float, nullable=True, comment="前收盘价")
    adjust_flag: Mapped[str] = mapped_column(String(10), nullable=True, comment="复权类型：不复权、前复权、后复权")
    

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
    
    # 新增字段
    avg_price: Mapped[float] = mapped_column(Float, nullable=True, comment="均价")
    adjust_flag: Mapped[str] = mapped_column(String(10), nullable=True, comment="复权类型：不复权、前复权、后复权")


class StockTick(BaseModel):
    """股票分笔数据表"""
    __tablename__ = "data_stock_tick"
    __table_args__ = ({'comment': '股票分笔数据表'})
    
    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False, comment="股票代码")
    trade_time: Mapped[str] = mapped_column(String(19), index=True, nullable=False, comment="交易时间，格式：YYYY-MM-DD HH:MM:SS")
    price: Mapped[float] = mapped_column(Float, comment="成交价格")
    volume: Mapped[int] = mapped_column(Integer, comment="成交量（手）")
    amount: Mapped[float] = mapped_column(Float, comment="成交额（元）")
    direction: Mapped[str] = mapped_column(String(10), comment="交易方向：买盘、卖盘、中性盘")
    price_change: Mapped[float] = mapped_column(Float, nullable=True, comment="价格变动")
