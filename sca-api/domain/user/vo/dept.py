
from pydantic import BaseModel, ConfigDict
from infra.core.data_types import DatetimeStr


class Dept(BaseModel):
    name: str
    dept_key: str
    disabled: bool = False
    order: int | None = None
    desc: str | None = None
    owner: str | None = None
    phone: str | None = None
    email: str | None = None

    parent_id: int | None = None


class DeptSimpleOut(Dept):
    model_config = ConfigDict(from_attributes=True)

    id: int
    create_datetime: DatetimeStr
    update_datetime: DatetimeStr


class DeptTreeListOut(DeptSimpleOut):
    model_config = ConfigDict(from_attributes=True)

    children: list[dict] = []

