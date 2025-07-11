from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr
from application.config.dev import SQLALCHEMY_DATABASE_URL


# 官方文档：https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.create_async_engine

# database_url  dialect+driver://username:password@host:port/database

# echo：如果为True，引擎将记录所有语句以及它们的参数列表的repr()到默认的日志处理程序，该处理程序默认为sys.stdout。如果设置为字符串"debug"，
# 结果行也将打印到标准输出。Engine的echo属性可以随时修改以打开和关闭日志记录；也可以使用标准的Python logging模块来直接控制日志记录。

# echo_pool=False：如果为True，连接池将记录信息性输出，如何时使连接失效以及何时将连接回收到默认的日志处理程序，该处理程序默认为sys.stdout。
# 如果设置为字符串"debug"，记录将包括池的检出和检入。也可以使用标准的Python logging模块来直接控制日志记录。

# pool_pre_ping：布尔值，如果为True，将启用连接池的"pre-ping"功能，该功能在每次检出时测试连接的活动性。

# pool_recycle=-1：此设置导致池在给定的秒数后重新使用连接。默认为-1，即没有超时。例如，将其设置为3600意味着在一小时后重新使用连接。
# 请注意，特别是MySQL会在检测到连接8小时内没有活动时自动断开连接（尽管可以通过MySQLDB连接自身和服务器配置进行配置）。

# pool_size=5：在连接池内保持打开的连接数。与QueuePool以及SingletonThreadPool一起使用。
# 对于QueuePool，pool_size设置为0表示没有限制；要禁用连接池，请将poolclass设置为NullPool。

# pool_timeout=30：在从池中获取连接之前等待的秒数。仅在QueuePool中使用。这可以是一个浮点数，但受Python时间函数的限制，可能在几十毫秒内不可靠

# max_overflow 参数用于配置连接池中允许的连接 "溢出" 数量。这个参数用于在高负载情况下处理连接请求的峰值。
# 当连接池的所有连接都在使用中时，如果有新的连接请求到达，连接池可以创建额外的连接来满足这些请求，最多创建的数量由 max_overflow 参数决定。


class DatabaseEngine:
    """
    数据库引擎类，负责创建和管理数据库连接
    """
    def __init__(self, database_url: str = SQLALCHEMY_DATABASE_URL):
        """
        初始化数据库引擎
        :param database_url: 数据库连接URL
        """
        self.engine = create_async_engine(
            database_url,
            echo=False,
            echo_pool=False,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=5,
            max_overflow=5,
            connect_args={}
        )


class SessionFactory:
    """
    会话工厂类，负责创建数据库会话
    """
    def __init__(self, engine):
        """
        初始化会话工厂
        :param engine: 数据库引擎
        """
        self.session_factory = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            expire_on_commit=True,
            class_=AsyncSession
        )
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        获取新的数据库会话
        :return: 异步生成器，生成数据库会话
        """
        async with self.session_factory() as session:
            # 创建一个新的事务，半自动 commit
            async with session.begin():
                yield session


# 创建数据库引擎实例
db_engine = DatabaseEngine()
# 创建会话工厂实例
session_factory_manager = SessionFactory(db_engine.engine)
# 导出会话工厂和引擎，保持向后兼容
async_engine = db_engine.engine
session_factory = session_factory_manager.session_factory


async def db_getter() -> AsyncGenerator[AsyncSession, None]:
    """
    获取主数据库会话

    数据库依赖项，它将在单个请求中使用，然后在请求完成后将其关闭。

    函数的返回类型被注解为 AsyncGenerator[int, None]，其中 AsyncSession 是生成的值的类型，而 None 表示异步生成器没有终止条件。
    """
    async for session in session_factory_manager.get_session():
        yield session
