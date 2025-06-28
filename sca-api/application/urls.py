from domain.user.utils.login import app as auth_app
from domain.user.views import app as auth_app
from domain.system.views import app as system_app
from domain.record.views import app as record_app
from domain.workplace.views import app as workplace_app
from domain.analysis.views import app as analysis_app
from domain.help.views import app as help_app
from domain.resource.views import app as resource_app

# 引入应用中的路由
urlpatterns = [
    {"ApiRouter": auth_app, "prefix": "/auth", "tags": ["系统认证"]},
    {"ApiRouter": auth_app, "prefix": "/auth", "tags": ["权限管理"]},
    {"ApiRouter": system_app, "prefix": "/system", "tags": ["系统管理"]},
    {"ApiRouter": record_app, "prefix": "/record", "tags": ["记录管理"]},
    {"ApiRouter": workplace_app, "prefix": "/workplace", "tags": ["工作区管理"]},
    {"ApiRouter": analysis_app, "prefix": "/analysis", "tags": ["数据分析管理"]},
    {"ApiRouter": help_app, "prefix": "/help", "tags": ["帮助中心管理"]},
    {"ApiRouter": resource_app, "prefix": "/resource", "tags": ["资源管理"]},
]
