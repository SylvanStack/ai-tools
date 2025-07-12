from motor.motor_asyncio import AsyncIOMotorDatabase

from infra.mongo.mongo_manage import MongoManage


class TaskRecordDal(MongoManage):

    def __init__(self, db: AsyncIOMotorDatabase):
        super(TaskRecordDal, self).__init__(db, "scheduler_task_record")