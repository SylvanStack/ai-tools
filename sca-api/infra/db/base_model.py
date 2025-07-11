from datetime import datetime

from sqlalchemy import DateTime, Integer, func, Boolean, inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.orm import Mapped, mapped_column


class TableNameGenerator:
    """
    表名生成器，负责生成表名
    """
    @staticmethod
    def generate_table_name(cls) -> str:
        """
        将类名转换为表名
        :param cls: 模型类
        :return: 表名
        """
        table_name = cls.__tablename__
        if not table_name:
            model_name = cls.__name__
            ls = []
            for index, char in enumerate(model_name):
                if char.isupper() and index != 0:
                    ls.append("_")
                ls.append(char)
            table_name = "".join(ls).lower()
        return table_name


class Base(AsyncAttrs, DeclarativeBase):
    """
    创建基本映射类
    稍后，我们将继承该类，创建每个 ORM 模型
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        将表名改为小写
        如果有自定义表名就取自定义，没有就取小写类名
        """
        return TableNameGenerator.generate_table_name(cls)


class ModelInspector:
    """
    模型检查器，负责检查模型属性
    """
    @staticmethod
    def get_column_attrs(cls) -> list:
        """
        获取模型中除 relationships 外的所有字段名称
        :param cls: 模型类
        :return: 字段名称列表
        """
        mapper = inspect(cls)
        return mapper.column_attrs.keys()

    @staticmethod
    def get_attrs(cls) -> list:
        """
        获取模型所有字段名称
        :param cls: 模型类
        :return: 字段名称列表
        """
        mapper = inspect(cls)
        return mapper.attrs.keys()

    @staticmethod
    def get_relationships_attrs(cls) -> list:
        """
        获取模型中 relationships 所有字段名称
        :param cls: 模型类
        :return: 关系字段名称列表
        """
        mapper = inspect(cls)
        return mapper.relationships.keys()


# 使用命令：alembic init alembic 初始化迁移数据库环境
# 这时会生成alembic文件夹 和 alembic.ini文件
class BaseModel(Base):
    """
    公共 ORM 模型，基表
    """
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='主键ID')
    create_datetime: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment='创建时间')
    update_datetime: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    delete_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='删除时间')
    is_delete: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否软删除")

    @classmethod
    def get_column_attrs(cls) -> list:
        """
        获取模型中除 relationships 外的所有字段名称
        :return: 字段名称列表
        """
        return ModelInspector.get_column_attrs(cls)

    @classmethod
    def get_attrs(cls) -> list:
        """
        获取模型所有字段名称
        :return: 字段名称列表
        """
        return ModelInspector.get_attrs(cls)

    @classmethod
    def get_relationships_attrs(cls) -> list:
        """
        获取模型中 relationships 所有字段名称
        :return: 关系字段名称列表
        """
        return ModelInspector.get_relationships_attrs(cls)
