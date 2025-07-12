from sqlalchemy.ext.asyncio import AsyncSession
from infra.db.crud import DalBase
from apps.help import models, schemas


class IssueCategoryDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(IssueCategoryDal, self).__init__(db=db, model=models.IssueCategory, schema=schemas.IssueCategorySimpleOut)
