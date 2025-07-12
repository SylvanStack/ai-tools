import json
import os

from fastapi import Request
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from application.settings import STATIC_ROOT, REDIS_DB_ENABLE
from apps.system import models, schemas
from infra.db.crud import DalBase
from infra.redis.redis_db import redis_getter
from infra.utils.file.file_manage import FileManage


class SettingsDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(SettingsDal, self).__init__(db=db, model=models.SystemSettings, schema=schemas.SettingsSimpleOut)

    async def get_tab_values(self, tab_id: int) -> dict:
        """
        获取系统配置标签下的信息
        """
        datas = await self.get_datas(limit=0, tab_id=tab_id, v_return_objs=True)
        result = {}
        for data in datas:
            if not data.disabled:
                result[data.config_key] = data.config_value
        return result

    async def update_datas(self, datas: dict, request: Request) -> None:
        """
        更新系统配置信息

        更新ico图标步骤：先将文件上传到本地，然后点击提交后，获取到文件地址，将上传的新文件覆盖原有文件
        原因：ico图标的路径是在前端的index.html中固定的，所以目前只能改变图片，不改变路径
        """
        for key, value in datas.items():
            if key == "web_ico":
                continue
            elif key == "web_ico_local_path":
                if not value:
                    continue
                ico = await self.get_data(config_key="web_ico", tab_id=1)
                web_ico = datas.get("web_ico")
                if ico.config_value == web_ico:
                    continue
                # 将上传的ico路径替换到static/system/favicon.ico文件
                await FileManage.async_copy_file(value, os.path.join(STATIC_ROOT, "system/favicon.ico"))
                sql = update(self.model).where(self.model.config_key == "web_ico").values(config_value=web_ico)
                await self.db.execute(sql)
            else:
                sql = update(self.model).where(self.model.config_key == str(key)).values(config_value=value)
                await self.db.execute(sql)
        if "wx_server_app_id" in datas and REDIS_DB_ENABLE:
            rd = redis_getter(request)
            await rd.client().set("wx_server", json.dumps(datas))
        elif "sms_access_key" in datas and REDIS_DB_ENABLE:
            rd = redis_getter(request)
            await rd.client().set('aliyun_sms', json.dumps(datas))

    async def get_base_config(self) -> dict:
        """
        获取系统基本信息
        """
        ignore_configs = ["wx_server_app_id", "wx_server_app_secret"]
        datas = await self.get_datas(limit=0, tab_id=("in", ["1", "9"]), disabled=False, v_return_objs=True)
        result = {}
        for config in datas:
            if config.config_key not in ignore_configs:
                result[config.config_key] = config.config_value
        return result