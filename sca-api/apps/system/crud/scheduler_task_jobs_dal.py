from motor.motor_asyncio import AsyncIOMotorDatabase

from infra.mongo.mongo_manage import MongoManage

class SchedulerTaskJobsDal(MongoManage):

    def __init__(self, db: AsyncIOMotorDatabase):
        super(SchedulerTaskJobsDal, self).__init__(db, "scheduler_task_jobs", is_object_id=False)
