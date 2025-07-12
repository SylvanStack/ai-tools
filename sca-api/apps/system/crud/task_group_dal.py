from motor.motor_asyncio import AsyncIOMotorDatabase

from infra.mongo.mongo_manage import MongoManage


class TaskGroupDal(MongoManage):

    def __init__(self, db: AsyncIOMotorDatabase):
        super(TaskGroupDal, self).__init__(db, "system_task_group")