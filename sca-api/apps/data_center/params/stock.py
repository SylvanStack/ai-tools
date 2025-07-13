from fastapi import Depends
from infra.core.dependencies import Paging, QueryParams





class StockInfoParams(QueryParams):
    """股票基本信息查询参数"""

    def __init__(
            self,
            params: Paging = Depends(),
            symbol: str = None,
            name: str = None,
            market: str = None,
            industry: str = None,
            is_active: bool = None
    ):
        super().__init__(params)
        self.v_order = "asc"
        self.v_order_field = "symbol"
        self.symbol = symbol
        self.name = ("like", name) if name else None
        self.market = market
        self.industry = industry
        self.is_active = is_active


class StockDailyParams(QueryParams):
    """股票日线数据查询参数"""

    def __init__(
            self,
            params: Paging = Depends(),
            symbol: str = None,
            stock_id: int = None,
            trade_date: str = None,
            start_date: str = None,
            end_date: str = None,
            adjust_flag: str = None
    ):
        super().__init__(params)
        self.v_order = "desc"
        self.v_order_field = "trade_date"
        self.symbol = symbol
        self.stock_id = stock_id
        self.trade_date = trade_date
        self.adjust_flag = adjust_flag
        
        # 处理日期范围查询
        if start_date:
            self.trade_date = (">=", start_date)
        if end_date:
            self.trade_date = ("<=", end_date)
        if start_date and end_date:
            self.trade_date = ("between", [start_date, end_date])


class StockMinuteParams(QueryParams):
    """股票分钟数据查询参数"""

    def __init__(
            self,
            params: Paging = Depends(),
            symbol: str = None,
            period: str = None,
            trade_time: str = None,
            start_time: str = None,
            end_time: str = None,
            adjust_flag: str = None
    ):
        super().__init__(params)
        self.v_order = "desc"
        self.v_order_field = "trade_time"
        self.symbol = symbol
        self.period = period
        self.trade_time = trade_time
        self.adjust_flag = adjust_flag
        
        # 处理时间范围查询
        if start_time:
            self.trade_time = (">=", start_time)
        if end_time:
            self.trade_time = ("<=", end_time)
        if start_time and end_time:
            self.trade_time = ("between", [start_time, end_time])


class StockTickParams(QueryParams):
    """股票分笔数据查询参数"""

    def __init__(
            self,
            params: Paging = Depends(),
            symbol: str = None,
            trade_time: str = None,
            start_time: str = None,
            end_time: str = None,
            direction: str = None
    ):
        super().__init__(params)
        self.v_order = "desc"
        self.v_order_field = "trade_time"
        self.symbol = symbol
        self.trade_time = trade_time
        self.direction = direction
        
        # 处理时间范围查询
        if start_time:
            self.trade_time = (">=", start_time)
        if end_time:
            self.trade_time = ("<=", end_time)
        if start_time and end_time:
            self.trade_time = ("between", [start_time, end_time]) 