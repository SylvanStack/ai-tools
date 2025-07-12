from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.system import models, schemas
from infra.db.crud import DalBase


class SettingsTabDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(SettingsTabDal, self).__init__(db, models.SystemSettingsTab, schemas.SettingsTabSimpleOut)

    async def get_classify_tab_values(self, classify: list[str], hidden: bool | None = False) -> dict:
        """
        获取系统配置分类下的标签信息
        """
        model = models.SystemSettingsTab
        options = [joinedload(model.settings)]
        datas = await self.get_datas(
            limit=0,
            v_options=options,
            classify=("in", classify),
            disabled=False,
            v_return_objs=True,
            hidden=hidden
        )
        return self.__generate_values(datas)

    async def get_tab_name_values(self, tab_names: list[str], hidden: bool | None = False) -> dict:
        """
        获取系统配置标签下的标签信息
        """
        model = models.SystemSettingsTab
        options = [joinedload(model.settings)]
        datas = await self.get_datas(
            limit=0,
            v_options=options,
            tab_name=("in", tab_names),
            disabled=False,
            v_return_objs=True,
            hidden=hidden
        )
        return self.__generate_values(datas)

    @classmethod
    def __generate_values(cls, datas: list[models.SystemSettingsTab]) -> dict:
        """
        生成字典值
        """
        return {
            tab.tab_name: {
                item.config_key: item.config_value
                for item in tab.settings
                if not item.disabled
            }
            for tab in datas
        }
