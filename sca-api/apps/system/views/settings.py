from fastapi import APIRouter, Depends, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession

from apps.system.crud.settings_dal import SettingsDal
from apps.system.crud.settings_tab_dal import SettingsTabDal
from apps.user.utils.current import FullAdminAuth, OpenAuth
from apps.user.utils.validation.auth import Auth
from infra.db.database import db_getter
from infra.utils.response import SuccessResponse

app = APIRouter()

###########################################################
#    系统配置管理
###########################################################
@app.post("/settings/tabs", summary="获取系统配置标签列表")
async def get_settings_tabs(classifys: list[str] = Body(...), auth: Auth = Depends(FullAdminAuth())):
    return SuccessResponse(await SettingsTabDal(auth.db).get_datas(limit=0, classify=("in", classifys)))


@app.get("/settings/tabs/values", summary="获取系统配置标签下的信息")
async def get_settings_tabs_values(tab_id: int, auth: Auth = Depends(FullAdminAuth())):
    return SuccessResponse(await SettingsDal(auth.db).get_tab_values(tab_id=tab_id))


@app.put("/settings/tabs/values", summary="更新系统配置信息")
async def put_settings_tabs_values(
        request: Request,
        datas: dict = Body(...),
        auth: Auth = Depends(FullAdminAuth())
):
    return SuccessResponse(await SettingsDal(auth.db).update_datas(datas, request))


@app.get("/settings/base/config", summary="获取系统基础配置", description="每次进入系统中时使用")
async def get_setting_base_config(db: AsyncSession = Depends(db_getter)):
    return SuccessResponse(await SettingsDal(db).get_base_config())


@app.get("/settings/privacy", summary="获取隐私协议")
async def get_settings_privacy(auth: Auth = Depends(OpenAuth())):
    return SuccessResponse((await SettingsDal(auth.db).get_data(config_key="web_privacy")).config_value)


@app.get("/settings/agreement", summary="获取用户协议")
async def get_settings_agreement(auth: Auth = Depends(OpenAuth())):
    return SuccessResponse((await SettingsDal(auth.db).get_data(config_key="web_agreement")).config_value)

