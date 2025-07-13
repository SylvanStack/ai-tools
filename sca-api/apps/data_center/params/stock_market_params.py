from fastapi import Depends
from infra.core.dependencies import Paging, QueryParams

class SseMarketParams(QueryParams):
    """上海证券交易所市场总貌查询参数"""

    def __init__(
            self,
            params: Paging = Depends(),
            date: str = None,
            start_date: str = None,
            end_date: str = None
    ):
        super().__init__(params)
        self.v_order = "desc"
        self.v_order_field = "date"
        self.date = date

        # 处理日期范围查询
        if start_date:
            self.date = (">=", start_date)
        if end_date:
            self.date = ("<=", end_date)
        if start_date and end_date:
            self.date = ("between", [start_date, end_date])


class SzseMarketParams(QueryParams):
    """深圳证券交易所市场总貌查询参数"""

    def __init__(
            self,
            params: Paging = Depends(),
            date: str = None,
            start_date: str = None,
            end_date: str = None
    ):
        super().__init__(params)
        self.v_order = "desc"
        self.v_order_field = "date"
        self.date = date

        # 处理日期范围查询
        if start_date:
            self.date = (">=", start_date)
        if end_date:
            self.date = ("<=", end_date)
        if start_date and end_date:
            self.date = ("between", [start_date, end_date])