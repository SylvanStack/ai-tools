# from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from infra.core.data_types import DatetimeStr


# 股票市场总貌相关模型
class StockMarket(BaseModel):
    market: str | None = None
    date: str | None = None
    total_stocks: int | None = None
    total_market_value: float | None = None
    circulating_market_value: float | None = None
    total_share_capital: float | None = None
    circulating_share_capital: float | None = None
    average_pe_ratio: float | None = None
    turnover_rate: float | None = None


class StockMarketOut(StockMarket):
    model_config = ConfigDict(from_attributes=True)

    id: int
    update_datetime: DatetimeStr
    create_datetime: DatetimeStr


class StockMarketListOut(StockMarketOut):
    model_config = ConfigDict(from_attributes=True)


# 股票基本信息相关模型
class StockInfo(BaseModel):
    symbol: str | None = None
    name: str | None = None
    market: str | None = None
    industry: str | None = None
    listing_date: str | None = None
    total_share_capital: float | None = None
    circulating_share_capital: float | None = None
    is_active: bool | None = None


class StockInfoOut(StockInfo):
    model_config = ConfigDict(from_attributes=True)

    id: int
    update_datetime: DatetimeStr
    create_datetime: DatetimeStr


class StockInfoListOut(StockInfoOut):
    model_config = ConfigDict(from_attributes=True)


class StockInfoSimpleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    label: str = Field(alias='name')
    value: str = Field(alias='symbol')
    id: int


# 股票日线数据相关模型
class StockDaily(BaseModel):
    stock_id: int | None = None
    symbol: str | None = None
    trade_date: str | None = None
    open_price: float | None = None
    close_price: float | None = None
    high_price: float | None = None
    low_price: float | None = None
    volume: int | None = None
    amount: float | None = None
    amplitude: float | None = None
    change_percent: float | None = None
    change_amount: float | None = None
    turnover_rate: float | None = None


class StockDailyOut(StockDaily):
    model_config = ConfigDict(from_attributes=True)

    id: int
    update_datetime: DatetimeStr
    create_datetime: DatetimeStr


class StockDailyListOut(StockDailyOut):
    model_config = ConfigDict(from_attributes=True)

    stock_info: StockInfoOut | None = None


# 股票分钟数据相关模型
class StockMinute(BaseModel):
    symbol: str | None = None
    trade_time: str | None = None
    period: str | None = None
    open_price: float | None = None
    close_price: float | None = None
    high_price: float | None = None
    low_price: float | None = None
    volume: int | None = None
    amount: float | None = None


class StockMinuteOut(StockMinute):
    model_config = ConfigDict(from_attributes=True)

    id: int
    update_datetime: DatetimeStr
    create_datetime: DatetimeStr


class StockMinuteListOut(StockMinuteOut):
    model_config = ConfigDict(from_attributes=True) 