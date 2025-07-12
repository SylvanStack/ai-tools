from fastapi import Depends
from infra.core.dependencies import Paging, QueryParams

class IssueCategoryParams(QueryParams):
    """
    列表分页
    """

    def __init__(
            self,
            params: Paging = Depends(),
            is_active: bool = None,
            platform: str = None,
            name: str = None
    ):
        super().__init__(params)
        self.v_order = "desc"
        self.v_order_field = "create_datetime"
        self.is_active = is_active
        self.platform = platform
        self.name = ("like", name)
