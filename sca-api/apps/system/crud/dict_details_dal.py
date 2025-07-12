from sqlalchemy.ext.asyncio import AsyncSession

from apps.system import models, schemas
from infra.db.crud import DalBase


class DictDetailsDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(DictDetailsDal, self).__init__(db=db, model=models.DictDetails, schema=schemas.DictDetailsSimpleOut)
