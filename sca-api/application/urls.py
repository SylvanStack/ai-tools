from apps.user.utils.login import app as auth_login_app
from apps.user.views import app as auth_views_app
from apps.system.views import app as system_app
from apps.record.views import app as record_app
from apps.help.views import app as help_app
from apps.resource.views import app as resource_app
from apps.data_center.views import app as data_center_app

# 引入应用中的路由
urlpatterns = [
    {"ApiRouter": auth_login_app, "prefix": "/auth", "tags": ["系统认证"]},
    {"ApiRouter": auth_views_app, "prefix": "/auth", "tags": ["权限管理"]},
    {"ApiRouter": system_app, "prefix": "/system", "tags": ["系统管理"]},
    {"ApiRouter": record_app, "prefix": "/record", "tags": ["记录管理"]},
    {"ApiRouter": help_app, "prefix": "/help", "tags": ["帮助中心管理"]},
    {"ApiRouter": resource_app, "prefix": "/resource", "tags": ["资源管理"]},
    {"ApiRouter": data_center_app, "prefix": "/data", "tags": ["数据中心"]},
]
