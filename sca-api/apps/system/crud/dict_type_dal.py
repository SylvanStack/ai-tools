from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.system import models, schemas
from infra.db.crud import DalBase


class DictTypeDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(DictTypeDal, self).__init__(db=db, model=models.DictType, schema=schemas.DictTypeSimpleOut)

    async def get_dicts_details(self, dict_types: list[str]) -> dict:
        """
        获取多个字典类型下的字典元素列表
        """
        data = {}
        options = [joinedload(self.model.details)]
        objs = await DictTypeDal(self.db).get_datas(
            limit=0,
            v_return_objs=True,
            v_options=options,
            dict_type=("in", dict_types)
        )
        for obj in objs:
            if not obj:
                data[obj.dict_type] = []
                continue
            else:
                data[obj.dict_type] = [schemas.DictDetailsSimpleOut.model_validate(i).model_dump() for i in obj.details]
        return data

    async def get_select_datas(self) -> list:
        """获取选择数据，全部数据"""
        sql = select(self.model)
        queryset = await self.db.execute(sql)
        return [schemas.DictTypeOptionsOut.model_validate(i).model_dump() for i in queryset.scalars().all()]