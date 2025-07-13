from fastapi import FastAPI
from apps.user.utils.login import app as auth_login_app
from apps.user.views.user import app as auth_user_app
from apps.user.views.role import app as auth_role_app
from apps.user.views.dept import app as auth_dept_app
from apps.user.views.menu import app as auth_menu_app
from apps.user.views.test import app as auth_test_app
# 系统模块
from apps.system.views.dict import app as system_dict_app
from apps.system.views.oss import app as system_oss_app
from apps.system.views.settings import app as system_settings_app
from apps.system.views.sms import app as system_sms_app
from apps.system.views.task import app as system_task_app
# 其他模块
from apps.help.views.issue_category import app as help_issue_category_app
from apps.help.views.issue import app as help_issue_app
from apps.record.views.views import app as record_app
from apps.resource.views.resource import app as resource_app
# 数据中心模块
from apps.data_center.views.stock_market import app as data_center_stock_market_app
from apps.data_center.views.stock_info import app as data_center_stock_info_app
from apps.data_center.views.stock_daily import app as data_center_stock_daily_app
from apps.data_center.views.stock_minute import app as data_center_stock_minute_app
from apps.data_center.views.stock_tick import app as data_center_stock_tick_app

from infra.swagger.docs import register_docs

# 创建应用
app = FastAPI(
    title="SCA-API",
    description="SCA-API",
    version="0.1.0",
)

# 注册swagger文档
register_docs(app)

# 注册路由
app.include_router(auth_login_app, prefix="/auth", tags=["登录认证"])
app.include_router(auth_user_app, prefix="/auth", tags=["用户管理"])
app.include_router(auth_role_app, prefix="/auth", tags=["角色管理"])
app.include_router(auth_dept_app, prefix="/auth", tags=["部门管理"])
app.include_router(auth_menu_app, prefix="/auth", tags=["菜单管理"])
app.include_router(auth_test_app, prefix="/auth", tags=["测试接口"])
# 系统模块
app.include_router(system_dict_app, prefix="/system", tags=["系统管理-字典管理"])
app.include_router(system_oss_app, prefix="/system", tags=["系统管理-存储管理"])
app.include_router(system_settings_app, prefix="/system", tags=["系统管理-系统设置"])
app.include_router(system_sms_app, prefix="/system", tags=["系统管理-短信管理"])
app.include_router(system_task_app, prefix="/system", tags=["系统管理-调度任务管理"])
# 其他模块
app.include_router(help_issue_category_app, prefix="/help", tags=["帮助中心-问题分类"])
app.include_router(help_issue_app, prefix="/help", tags=["帮助中心-问题管理"])
app.include_router(record_app, prefix="/record", tags=["记录管理"])
app.include_router(resource_app, prefix="/resource", tags=["资源管理"])
# 数据中心模块
app.include_router(data_center_stock_market_app, prefix="/data-center", tags=["数据中心-股票市场总貌"])
app.include_router(data_center_stock_info_app, prefix="/data-center", tags=["数据中心-股票基本信息"])
app.include_router(data_center_stock_daily_app, prefix="/data-center", tags=["数据中心-股票日线数据"])
app.include_router(data_center_stock_minute_app, prefix="/data-center", tags=["数据中心-股票分钟数据"])
app.include_router(data_center_stock_tick_app, prefix="/data-center", tags=["数据中心-股票分笔数据"])
