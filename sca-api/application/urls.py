# 登陆/注册
from apps.user.utils.login import app as auth_login_app
# 权限管理
from apps.user.views.user import app as auth_user_app
from apps.user.views.role import app as auth_role_app
from apps.user.views.dept import app as auth_dept_app
from apps.user.views.menu import app as auth_menu_app
from apps.user.views.test import app as auth_test_app
# 系统配置关
from apps.system.views.dict import app as system_dict_app
from apps.system.views.oss import app as system_oss_app
from apps.system.views.settings import app as system_settings_app
from apps.system.views.sms import app as system_sms_app
from apps.system.views.task import app as system_task_app
# 操作记录
from apps.record.views import app as record_app
# 帮助中心
from apps.help.views.issue_category import app as help_category_app
from apps.help.views.issue import app as help_issue_app
# 图片资源管理
from apps.resource.views.resource import app as resource_app
# 股票-数据中心
from apps.data_center.views.stock_market import app as data_center_app

# 引入应用中的路由
urlpatterns = [
    {"ApiRouter": auth_login_app, "prefix": "/auth", "tags": ["系统认证"]},
    {"ApiRouter": auth_user_app, "prefix": "/auth", "tags": ["用户管理"]},
    {"ApiRouter": auth_role_app, "prefix": "/auth", "tags": ["角色管理"]},
    {"ApiRouter": auth_dept_app, "prefix": "/auth", "tags": ["部门管理"]},
    {"ApiRouter": auth_menu_app, "prefix": "/auth", "tags": ["菜单管理"]},
    {"ApiRouter": auth_test_app, "prefix": "/auth", "tags": ["测试"]},
    {"ApiRouter": system_dict_app, "prefix": "/system", "tags": ["系统管理-字典管理"]},
    {"ApiRouter": system_oss_app, "prefix": "/system", "tags": ["系统管理-存储管理"]},
    {"ApiRouter": system_settings_app, "prefix": "/system", "tags": ["系统管理-系统设置"]},
    {"ApiRouter": system_sms_app, "prefix": "/system", "tags": ["系统管理-短信管理"]},
    {"ApiRouter": system_task_app, "prefix": "/system", "tags": ["系统管理-调度任务管理"]},
    {"ApiRouter": record_app, "prefix": "/record", "tags": ["记录管理"]},
    {"ApiRouter": help_category_app, "prefix": "/help", "tags": ["帮助中心-问题分类管理"]},
    {"ApiRouter": help_issue_app, "prefix": "/help", "tags": ["帮助中心-问题管理"]},
    {"ApiRouter": resource_app, "prefix": "/resource", "tags": ["资源管理"]},
    {"ApiRouter": data_center_app, "prefix": "/data", "tags": ["数据中心"]},
]
