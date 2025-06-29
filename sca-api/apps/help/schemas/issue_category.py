

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from infra.core.data_types import DatetimeStr
from apps.user.schemas import UserSimpleOut


class IssueCategory(BaseModel):
    name: str | None = None
    platform: str | None = None
    is_active: bool | None = None

    create_user_id: int | None = None


class IssueCategorySimpleOut(IssueCategory):
    model_config = ConfigDict(from_attributes=True)

    id: int
    update_datetime: DatetimeStr
    create_datetime: DatetimeStr


class IssueCategoryListOut(IssueCategorySimpleOut):
    model_config = ConfigDict(from_attributes=True)

    create_user: UserSimpleOut


class IssueCategoryOptionsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    label: str = Field(alias='name')
    value: int = Field(alias='id')

