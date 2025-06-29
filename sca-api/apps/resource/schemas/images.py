from pydantic import BaseModel, ConfigDict
from infra.core.data_types import DatetimeStr
from apps.user.schemas import UserSimpleOut


class Images(BaseModel):
    filename: str
    image_url: str

    create_user_id: int


class ImagesSimpleOut(Images):
    model_config = ConfigDict(from_attributes=True)

    id: int
    create_datetime: DatetimeStr
    update_datetime: DatetimeStr


class ImagesOut(ImagesSimpleOut):
    model_config = ConfigDict(from_attributes=True)

    create_user: UserSimpleOut
