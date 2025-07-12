from sqlalchemy.ext.asyncio import AsyncSession
from infra.db.crud import DalBase
from apps.help import models, schemas


class IssueDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(IssueDal, self).__init__(db=db, model=models.Issue, schema=schemas.IssueSimpleOut)

    async def add_view_number(self, data_id: int) -> None:
        """
        更新常见问题查看次数+1
        """
        obj: models.Issue = await self.get_data(data_id)
        obj.view_number = obj.view_number + 1 if obj.view_number else 1
        await self.flush(obj)