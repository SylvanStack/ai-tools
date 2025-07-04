


from pydantic import BaseModel, ConfigDict
from infra.core.data_types import DatetimeStr


class SettingsTab(BaseModel):
    title: str
    classify: str
    tab_label: str
    tab_name: str
    hidden: bool


class SettingsTabSimpleOut(SettingsTab):
    model_config = ConfigDict(from_attributes=True)

    id: int
    create_datetime: DatetimeStr
    update_datetime: DatetimeStr

