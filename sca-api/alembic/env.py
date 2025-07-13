from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
import sys
from dotenv import load_dotenv

from infra.db.base_model import Base

# 加载环境变量
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# 添加当前项目路径到环境变量
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 从环境变量中读取数据库连接参数
section = config.config_ini_section
config.set_section_option(section, "sqlalchemy.url",
                          f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '123456')}@"
                          f"{os.getenv('DB_HOST', '127.0.0.1')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'sca-api')}")

# 导入项目中的基本映射类，与 需要迁移的 ORM 模型
# 导入所有模块的模型
# data_center 模块
from apps.data_center.models import SseMarket, SzseMarket, StockInfo, StockDaily, StockMinute, StockTick
# record 模块
from apps.record.models import LoginRecord, SMSSendRecord
# user 模块
from apps.user.models import User, Role, Menu, Dept, auth_user_roles, auth_user_depts, auth_role_depts
# system 模块
from apps.system.models.settings import SystemSettings, SystemSettingsTab
from apps.system.models.dict import DictType, DictDetails
# resource 模块
from apps.resource.models.images import Images
# help 模块
from apps.help.models import Issue, IssueCategory

# 修改配置中的参数
target_metadata = Base.metadata

# 检查是否需要跳过删除表操作
SKIP_DROP_TABLES = os.environ.get('ALEMBIC_SKIP_DROP_TABLES', '').lower() == 'true'


# 自定义表比较函数，用于跳过删除表操作
def include_object(object, name, type_, reflected, compare_to):
    if SKIP_DROP_TABLES and type_ == "table" and reflected and compare_to is None:
        # 如果设置了跳过删除表，且当前操作是删除表，则跳过
        print(f"跳过删除表 {name}")
        return False
    return True


def run_migrations_offline():
    """
    以"脱机"模式运行迁移。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 是否检查字段类型，字段长度
        compare_server_default=True,  # 是否比较在数据库中的默认值
        include_object=include_object  # 使用自定义函数决定是否包含对象
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    以"在线"模式运行迁移。
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 是否检查字段类型，字段长度
            compare_server_default=True,  # 是否比较在数据库中的默认值
            include_object=include_object  # 使用自定义函数决定是否包含对象
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    print("offline")
    run_migrations_offline()
else:
    print("online")
    run_migrations_online()
