from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from apps.system import schemas
from apps.system.crud.task_dal import TaskDal
from apps.system.crud.task_group_dal import TaskGroupDal
from apps.system.crud.task_record_dal import TaskRecordDal
from apps.system.params import TaskParams
from apps.system.params.task import TaskRecordParams
from apps.user.utils.current import AllUserAuth
from apps.user.utils.validation.auth import Auth
from infra.mongo.mongo_db import mongo_getter
from infra.redis.redis_db import redis_getter
from infra.utils.response import SuccessResponse

app = APIRouter()



###########################################################
#    定时任务管理
###########################################################
@app.get("/tasks", summary="获取定时任务列表")
async def get_tasks(
        p: TaskParams = Depends(),
        db: AsyncIOMotorDatabase = Depends(mongo_getter),
        auth: Auth = Depends(AllUserAuth())
):
    datas, count = await TaskDal(db).get_tasks(**p.dict())
    return SuccessResponse(datas, count=count)


@app.post("/tasks", summary="添加定时任务")
async def post_tasks(
        data: schemas.Task,
        db: AsyncIOMotorDatabase = Depends(mongo_getter),
        rd: Redis = Depends(redis_getter),
        auth: Auth = Depends(AllUserAuth())
):
    return SuccessResponse(await TaskDal(db).create_task(rd, data))


@app.put("/tasks", summary="更新定时任务")
async def put_tasks(
        _id: str,
        data: schemas.Task,
        db: AsyncIOMotorDatabase = Depends(mongo_getter),
        rd: Redis = Depends(redis_getter),
        auth: Auth = Depends(AllUserAuth())
):
    return SuccessResponse(await TaskDal(db).put_task(rd, _id, data))


@app.delete("/tasks", summary="删除单个定时任务")
async def delete_task(
        _id: str,
        db: AsyncIOMotorDatabase = Depends(mongo_getter),
        auth: Auth = Depends(AllUserAuth())
):
    return SuccessResponse(await TaskDal(db).delete_task(_id))


@app.get("/task", summary="获取定时任务详情")
async def get_task(
        _id: str,
        db: AsyncIOMotorDatabase = Depends(mongo_getter),
        auth: Auth = Depends(AllUserAuth())
):
    return SuccessResponse(await TaskDal(db).get_task(_id, v_schema=schemas.TaskSimpleOut))


@app.post("/task", summary="执行一次定时任务")
async def run_once_task(
        _id: str,
        db: AsyncIOMotorDatabase = Depends(mongo_getter),
        rd: Redis = Depends(redis_getter),
        auth: Auth = Depends(AllUserAuth())
):
    return SuccessResponse(await TaskDal(db).run_once_task(rd, _id))


###########################################################
#    定时任务分组管理
###########################################################
@app.get("/task/group/options", summary="获取定时任务分组选择项列表")
async def get_task_group_options(db: AsyncIOMotorDatabase = Depends(mongo_getter), auth: Auth = Depends(AllUserAuth())):
    return SuccessResponse(await TaskGroupDal(db).get_datas(limit=0))


###########################################################
#    定时任务调度日志
###########################################################
@app.get("/task/records", summary="获取定时任务调度日志列表")
async def get_task_records(
        p: TaskRecordParams = Depends(),
        db: AsyncIOMotorDatabase = Depends(mongo_getter),
        auth: Auth = Depends(AllUserAuth())
):
    count = await TaskRecordDal(db).get_count(**p.to_count())
    datas = await TaskRecordDal(db).get_datas(**p.dict())
    return SuccessResponse(datas, count=count)
