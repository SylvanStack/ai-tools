import json
from enum import Enum
from typing import Any

from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from application.settings import SUBSCRIBE
from apps.system import schemas
from infra.exception.exception import CustomException
from infra.mongo.mongo_manage import MongoManage
from infra.utils import status


class TaskDal(MongoManage):

    class JobOperation(Enum):
        add = "add_job"

    def __init__(self, db: AsyncIOMotorDatabase):
        super(TaskDal, self).__init__(db, "system_task", schemas.TaskSimpleOut)

    async def get_task(
            self,
            _id: str = None,
            v_return_none: bool = False,
            v_schema: Any = None,
            **kwargs
    ) -> dict | None:
        """
        获取单个数据，默认使用 ID 查询，否则使用关键词查询

        包括临时字段 last_run_datetime，is_active
        is_active: 只有在 scheduler_task_jobs 任务运行表中存在相同 _id 才表示任务添加成功，任务状态才为 True
        last_run_datetime: 在 scheduler_task_record 中获取该任务最近一次执行完成的时间

        :param _id: 数据 ID
        :param v_return_none: 是否返回空 None，否则抛出异常，默认抛出异常
        :param v_schema: 指定使用的序列化对象
        """
        if _id:
            kwargs["_id"] = ("ObjectId", _id)

        params = self.filter_condition(**kwargs)
        pipeline = [
            {
                '$addFields': {
                    'str_id': {'$toString': '$_id'}
                }
            },
            {
                '$lookup': {
                    'from': 'scheduler_task_jobs',
                    'localField': 'str_id',
                    'foreignField': '_id',
                    'as': 'matched_jobs'
                }
            },
            {
                '$lookup': {
                    'from': 'scheduler_task_record',
                    'localField': 'str_id',
                    'foreignField': 'job_id',
                    'as': 'matched_records'
                }
            },
            {
                '$addFields': {
                    'is_active': {
                        '$cond': {
                            'if': {'$ne': ['$matched_jobs', []]},
                            'then': True,
                            'else': False
                        }
                    },
                    'last_run_datetime': {
                        '$ifNull': [
                            {'$arrayElemAt': ['$matched_records.create_datetime', -1]},
                            None
                        ]
                    }
                }
            },
            {
                '$project': {
                    'matched_records': 0,
                    'matched_jobs': 0
                }
            },
            {
                '$match': params
            },
            {
                '$facet': {
                    'documents': [
                        {'$limit': 1},
                    ]
                }
            }
        ]
        # 执行聚合查询
        cursor = self.collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        data = result[0]['documents']
        if not data and v_return_none:
            return None
        elif not data:
            raise CustomException("未查找到对应数据", code=status.HTTP_404_NOT_FOUND)
        data = data[0]
        if data and v_schema:
            return jsonable_encoder(v_schema(**data))
        return data

    async def get_tasks(
            self,
            page: int = 1,
            limit: int = 10,
            v_schema: Any = None,
            v_order: str = None,
            v_order_field: str = None,
            **kwargs
    ) -> tuple:
        """
        获取任务信息列表

        添加了两个临时字段
        is_active: 只有在 scheduler_task_jobs 任务运行表中存在相同 _id 才表示任务添加成功，任务状态才为 True
        last_run_datetime: 在 scheduler_task_record 中获取该任务最近一次执行完成的时间
        """
        v_order_field = v_order_field if v_order_field else 'create_datetime'
        v_order = -1 if v_order in self.ORDER_FIELD else 1
        params = self.filter_condition(**kwargs)
        pipeline = [
            {
                '$addFields': {
                    'str_id': {'$toString': '$_id'}
                }
            },
            {
                '$lookup': {
                    'from': 'scheduler_task_jobs',
                    'localField': 'str_id',
                    'foreignField': '_id',
                    'as': 'matched_jobs'
                }
            },
            {
                '$lookup': {
                    'from': 'scheduler_task_record',
                    'localField': 'str_id',
                    'foreignField': 'job_id',
                    'as': 'matched_records'
                }
            },
            {
                '$addFields': {
                    'is_active': {
                        '$cond': {
                            'if': {'$ne': ['$matched_jobs', []]},
                            'then': True,
                            'else': False
                        }
                    },
                    'last_run_datetime': {
                        '$ifNull': [
                            {'$arrayElemAt': ['$matched_records.create_datetime', -1]},
                            None
                        ]
                    }
                }
            },
            {
                '$project': {
                    'matched_records': 0,
                    'matched_jobs': 0
                }
            },
            {
                '$match': params
            },
            {
                '$facet': {
                    'documents': [
                        {'$sort': {v_order_field: v_order}},
                        {'$limit': limit},
                        {'$skip': (page - 1) * limit}
                    ],
                    'count': [{'$count': 'total'}]
                }
            }
        ]

        # 执行聚合查询
        cursor = self.collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        datas = result[0]['documents']
        count = result[0]['count'][0]['total'] if result[0]['count'] else 0
        if count == 0:
            return [], 0
        elif v_schema:
            datas = [jsonable_encoder(v_schema(**data)) for data in datas]
        elif self.schema:
            datas = [jsonable_encoder(self.schema(**data)) for data in datas]
        return datas, count

    async def add_task(self, rd: Redis, data: dict) -> int:
        """
        添加任务到消息队列

        使用消息无保留策略：无保留是指当发送者向某个频道发送消息时，如果没有订阅该频道的调用方，就直接将该消息丢弃。

        :param rd: redis 对象
        :param data: 行数据字典
        :return: 接收到消息的订阅者数量。
        """
        exec_strategy = data.get("exec_strategy")
        job_params = {
            "name": data.get("_id"),
            "job_class": data.get("job_class"),
            "expression": data.get("expression")
        }
        if exec_strategy == "interval" or exec_strategy == "cron":
            job_params["start_date"] = data.get("start_date")
            job_params["end_date"] = data.get("end_date")
        message = {
            "operation": self.JobOperation.add.value,
            "task": {
                "exec_strategy": data.get("exec_strategy"),
                "job_params": job_params
            }
        }
        return await rd.publish(SUBSCRIBE, json.dumps(message).encode('utf-8'))

    async def create_task(self, rd: Redis, data: schemas.Task) -> dict:
        """
        创建任务
        """
        data_dict = data.model_dump()
        is_active = data_dict.pop('is_active')
        insert_result = await super().create_data(data_dict)
        obj = await self.get_task(insert_result.inserted_id, v_schema=schemas.TaskSimpleOut)

        # 如果分组不存在则新增分组
        group = await TaskGroupDal(self.db).get_data(value=data.group, v_return_none=True)
        if not group:
            await TaskGroupDal(self.db).create_data({"value": data.group})

        result = {
            "subscribe_number": 0,
            "is_active": is_active
        }

        if is_active:
            # 创建任务成功后, 如果任务状态为 True，则向消息队列中发送任务
            result['subscribe_number'] = await self.add_task(rd, obj)
        return result

    async def put_task(self, rd: Redis, _id: str, data: schemas.Task) -> dict:
        """
        更新任务
        """
        data_dict = data.model_dump()
        is_active = data_dict.pop('is_active')
        await super(TaskDal, self).put_data(_id, data)
        obj: dict = await self.get_task(_id, v_schema=schemas.TaskSimpleOut)

        # 如果分组不存在则新增分组
        group = await TaskGroupDal(self.db).get_data(value=data.group, v_return_none=True)
        if not group:
            await TaskGroupDal(self.db).create_data({"value": data.group})

        try:
            # 删除正在运行中的 Job
            await SchedulerTaskJobsDal(self.db).delete_data(_id)
        except CustomException as e:
            pass

        result = {
            "subscribe_number": 0,
            "is_active": is_active
        }

        if is_active:
            # 更新任务成功后, 如果任务状态为 True，则向消息队列中发送任务
            result['subscribe_number'] = await self.add_task(rd, obj)
        return result

    async def delete_task(self, _id: str) -> bool:
        """
        删除任务
        """
        result = await super(TaskDal, self).delete_data(_id)

        try:
            # 删除正在运行中的 Job
            await SchedulerTaskJobsDal(self.db).delete_data(_id)
        except CustomException as e:
            pass
        return result

    async def run_once_task(self, rd: Redis, _id: str) -> int:
        """
        执行一次任务
        """
        obj: dict = await self.get_data(_id, v_schema=schemas.TaskSimpleOut)
        message = {
            "operation": self.JobOperation.add.value,
            "task": {
                "exec_strategy": "once",
                "job_params": {
                    "name": obj.get("_id"),
                    "job_class": obj.get("job_class")
                }
            }
        }
        return await rd.publish(SUBSCRIBE, json.dumps(message).encode('utf-8'))

