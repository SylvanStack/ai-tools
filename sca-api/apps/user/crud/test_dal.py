from sqlalchemy import select, false, and_
from sqlalchemy.exc import StatementError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, aliased
from sqlalchemy.orm.strategy_options import contains_eager

from apps.help import models as help_models
from apps.user import models
from infra.db.crud import DalBase


class TestDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(TestDal, self).__init__(db=db, model=models.User)

    async def test_session_cache(self):
        """
        SQLAlchemy 会话（Session）缓存机制：
        当你通过一个会话查询数据库时，SQLAlchemy 首先检查这个对象是否已经在会话缓存中。如果是，它会直接从缓存中返回对象，而不是从数据库重新加载。
        在一个会话中，对于具有相同主键的实体，会话缓存确保只有一个唯一的对象实例。这有助于维护数据的一致性。

        会话（Session）缓存：https://blog.csdn.net/k_genius/article/details/135491059
        :return:
        """
        print("==================================会话缓存====================================")
        await self.test_session_cache1()
        print("=============查询出单个对象结果后，即使没有通过.访问属性，同样会产生缓存=============")
        await self.test_session_cache2()
        print("=============================数据列表会话缓存==================================")
        await self.test_session_cache3()
        print("=============================expire 单个对象过期==============================")
        await self.test_session_cache4()
        print("=========expire 单个对象过期后，重新访问之前对象的属性也会重新查询数据库，但是不会重新加载关系==========")
        await self.test_session_cache5()

    async def test_session_cache1(self):
        """
        SQLAlchemy 会话（Session）缓存机制：
        当你通过一个会话查询数据库时，SQLAlchemy 首先检查这个对象是否已经在会话缓存中。如果是，它会直接从缓存中返回对象，而不是从数据库重新加载。
        在一个会话中，对于具有相同主键的实体，会话缓存确保只有一个唯一的对象实例。这有助于维护数据的一致性。

        会话（Session）缓存：https://blog.csdn.net/k_genius/article/details/135491059

        示例：会话缓存

        :return:
        """
        # 第一次查询，并加载用户的所有关联部门项
        sql1 = select(models.User).where(models.User.id == 1).options(joinedload(models.User.depts))
        queryset1 = await self.db.scalars(sql1)
        user1 = queryset1.unique().first()
        print(f"用户编号：{user1.id} 用户姓名：{user1.name} 关联部门 {[i.name for i in user1.depts]}")

        # 第二次即使没有加载用户关联的部门，同样可以访问，因为这里会默认从会话缓存中获取
        sql2 = select(models.User).where(models.User.id == 1)
        queryset2 = await self.db.scalars(sql2)
        user2 = queryset2.first()
        print(f"用户编号：{user2.id} 用户姓名：{user2.name} 关联部门 {[i.name for i in user2.depts]}")

    async def test_session_cache2(self):
        """
        SQLAlchemy 会话（Session）缓存机制：
        当你通过一个会话查询数据库时，SQLAlchemy 首先检查这个对象是否已经在会话缓存中。如果是，它会直接从缓存中返回对象，而不是从数据库重新加载。
        在一个会话中，对于具有相同主键的实体，会话缓存确保只有一个唯一的对象实例。这有助于维护数据的一致性。

        会话（Session）缓存：https://blog.csdn.net/k_genius/article/details/135491059

        示例：查询出单个对象结果后，即使没有通过.访问属性，同样会产生缓存

        :return:
        """
        # 第一次查询，并加载用户的所有关联部门项，但是不访问用户的属性
        sql1 = select(models.User).where(models.User.id == 1).options(joinedload(models.User.depts))
        queryset1 = await self.db.scalars(sql1)
        user1 = queryset1.unique().first()
        print(f"没有访问属性，也会产生缓存")

        # 第二次即使没有加载用户关联的部门，同样可以访问，因为这里会默认从会话缓存中获取
        sql2 = select(models.User).where(models.User.id == 1)
        queryset2 = await self.db.scalars(sql2)
        user2 = queryset2.first()
        print(f"用户编号：{user2.id} 用户姓名：{user2.name} 关联部门 {[i.name for i in user2.depts]}")

    async def test_session_cache3(self):
        """
        SQLAlchemy 会话（Session）缓存机制：
        当你通过一个会话查询数据库时，SQLAlchemy 首先检查这个对象是否已经在会话缓存中。如果是，它会直接从缓存中返回对象，而不是从数据库重新加载。
        在一个会话中，对于具有相同主键的实体，会话缓存确保只有一个唯一的对象实例。这有助于维护数据的一致性。

        会话（Session）缓存：https://blog.csdn.net/k_genius/article/details/135491059

        示例：数据列表会话缓存

        :return:
        """
        # 第一次查询出所有用户，并加载用户的所有关联部门项
        sql1 = select(models.User).options(joinedload(models.User.depts))
        queryset1 = await self.db.scalars(sql1)
        datas1 = queryset1.unique().all()
        for data in datas1:
            print(f"用户编号：{data.id} 用户姓名：{data.name} 关联部门 {[i.name for i in data.depts]}")

        # 第二次即使没有加载用户关联的部门，同样可以访问，因为这里会默认从会话缓存中获取
        sql2 = select(models.User)
        queryset2 = await self.db.scalars(sql2)
        datas2 = queryset2.all()
        for data in datas2:
            print(f"用户编号：{data.id} 用户姓名：{data.name} 关联部门 {[i.name for i in data.depts]}")

    async def test_session_cache4(self):
        """
        SQLAlchemy 会话（Session）缓存机制：
        当你通过一个会话查询数据库时，SQLAlchemy 首先检查这个对象是否已经在会话缓存中。如果是，它会直接从缓存中返回对象，而不是从数据库重新加载。
        在一个会话中，对于具有相同主键的实体，会话缓存确保只有一个唯一的对象实例。这有助于维护数据的一致性。

        会话（Session）缓存：https://blog.csdn.net/k_genius/article/details/135491059

        示例：expire 单个对象过期

        :return:
        """
        # 第一次查询，并加载用户的所有关联部门项
        sql1 = select(models.User).where(models.User.id == 1).options(joinedload(models.User.depts))
        queryset1 = await self.db.scalars(sql1)
        user1 = queryset1.unique().first()
        print(f"用户编号：{user1.id} 用户姓名：{user1.name} 关联部门 {[i.name for i in user1.depts]}")

        # 使当前会话（Session）中的 user1 对象过期，再次访问就会重新查询数据库数据
        self.db.expire(user1)

        # 第二次查询会发现会话中没有该对象的缓存，会重新在数据库中查询
        sql2 = select(models.User).where(models.User.id == 1)
        queryset2 = await self.db.scalars(sql2)
        user2 = queryset2.first()
        try:
            print(f"用户编号：{user2.id} 用户姓名：{user2.name} 关联部门 {[i.name for i in user2.depts]}")
        except StatementError:
            print("访问部门报错了！！！！！")

    async def test_session_cache5(self):
        """
        SQLAlchemy 会话（Session）缓存机制：
        当你通过一个会话查询数据库时，SQLAlchemy 首先检查这个对象是否已经在会话缓存中。如果是，它会直接从缓存中返回对象，而不是从数据库重新加载。
        在一个会话中，对于具有相同主键的实体，会话缓存确保只有一个唯一的对象实例。这有助于维护数据的一致性。

        会话（Session）缓存：https://blog.csdn.net/k_genius/article/details/135491059

        示例：expire 单个对象过期后，重新访问之前对象的属性也会重新查询数据库，但是不会重新加载关系

        :return:
        """
        # 第一次查询，并加载用户的所有关联部门项
        sql = select(models.User).where(models.User.id == 1).options(joinedload(models.User.depts))
        queryset = await self.db.scalars(sql)
        user = queryset.unique().first()
        print(f"用户编号：{user.id} 用户姓名：{user.name} 关联部门 {[i.name for i in user.depts]}")

        # 使当前会话（Session）中的 user9 对象过期，再次访问就会重新查询数据库数据
        self.db.expire(user)

        # 第二次查询会发现会话中没有该对象的缓存，会重新在数据库中查询，但是不会重新加载关系
        try:
            print(f"用户编号：{user.id} 用户姓名：{user.name} 关联部门 {[i.name for i in user.depts]}")
        except StatementError:
            print("访问部门报错了！！！！！")

    async def test_join_form(self):
        """
        join_form 使用示例：通过关联表的查询条件反查询出主表的数据

        官方描述：在当前 Select 的左侧不符合我们想要从中进行连接的情况下，可以使用 Select.join_from() 方法
        官方文档：https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#setting-the-leftmost-from-clause-in-a-join

        查询条件：获取指定用户所关联的所有部门列表数据，只返回关联的部门列表数据
        :return:
        """
        # 设定用户编号为：1
        user_id = 1

        sql = select(models.Dept).where(models.Dept.is_delete == false())
        sql = sql.join_from(models.User, models.User.depts).where(models.User.id == user_id)
        queryset = await self.db.scalars(sql)
        result = queryset.unique().all()
        for dept in result:
            print(f"部门编号：{dept.id} 部门名称：{dept.name} 部门负责人：{dept.owner}")

        # 转换后的 SQL：
        # SELECT
        # 	_auth_dept.NAME,
        # 	_auth_dept.dept_key,
        # 	_auth_dept.disabled,
        # 	_auth_dept.order,
        # 	_auth_dept.desc,
        # 	_auth_dept.OWNER,
        # 	_auth_dept.phone,
        # 	_auth_dept.email,
        # 	_auth_dept.parent_id,
        # 	_auth_dept.id,
        # 	_auth_dept.create_datetime,
        # 	_auth_dept.update_datetime,
        # 	_auth_dept.delete_datetime,
        # 	_auth_dept.is_delete
        # FROM
        # 	_auth_user
        # 	JOIN auth_user_depts ON _auth_user.id = auth_user_depts.user_id
        # 	JOIN _auth_dept ON _auth_dept.id = auth_user_depts.dept_id
        # WHERE
        # 	_auth_dept.is_delete = FALSE
        # 	AND _auth_user.id = 1

    async def test_left_join(self):
        """
        多对多左连接查询示例：
        查询出所有用户信息，并加载用户关联所有部门，左连接条件：只需要查询出该用户关联的部门负责人为"张伟"的部门即可，其他部门不需要显示，
        :return:
        """
        # 封装查询语句
        dept_alias = aliased(models.Dept)
        v_options = [contains_eager(self.model.depts, alias=dept_alias)]
        v_outer_join = [
            [models.auth_user_depts, self.model.id == models.auth_user_depts.c.user_id],
            [dept_alias, and_(dept_alias.id == models.auth_user_depts.c.dept_id, dept_alias.owner == "张伟")]
        ]
        datas: list[models.User] = await self.get_datas(
            limit=0,
            v_outer_join=v_outer_join,
            v_options=v_options,
            v_return_objs=True,
            v_expire_all=True
        )
        for data in datas:
            print(f"用户编号：{data.id} 用户名称：{data.name} 共查询出关联的部门负责人为‘张伟’的部门有如下：")
            for dept in data.depts:
                print(f"      部门编号：{dept.id} 部门名称：{dept.name} 部门负责人：{dept.owner}")

        # 原查询语句：
        # DeptAlias = aliased(models.Dept)
        # sql = select(self.model).where(self.model.is_delete == false())
        # sql = sql.options(contains_eager(self.model.depts, alias=DeptAlias))
        # sql = sql.outerjoin(models.auth_user_depts, self.model.id == models.auth_user_depts.c.user_id)
        # sql = sql.outerjoin(
        #     DeptAlias,
        #     and_(DeptAlias.id == models.auth_user_depts.c.dept_id, DeptAlias.owner == "张伟")
        # )
        # self.db.expire_all()
        # queryset = await self.db.scalars(sql)
        # result = queryset.unique().all()
        # for data in result:
        #     print(f"用户编号：{data.id} 用户名称：{data.name} 共查询出关联的部门负责人为‘张伟’的部门有如下：")
        #     for dept in data.depts:
        #         print(f"      部门编号：{dept.id} 部门名称：{dept.name} 部门负责人：{dept.owner}")

    async def get_user_depts(self):
        """
        获取用户部门列表
        :return:
        """
        sql1 = select(models.User).options(joinedload(models.User.depts))
        queryset1 = await self.db.scalars(sql1)
        datas1 = queryset1.unique().all()
        for data in datas1:
            print(f"用户编号：{data.id} 用户姓名：{data.name} 关联部门 {[i.name for i in data.depts]}")

    async def relationship_where_operations_any(self):
        """
        关系运算符操作：any 方法使用示例
        官方文档： https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#relationship-where-operators

        any 方法用于一对多关系中，允许在 any 方法中指定一个条件，该条件会生成一个 SQL 表达式，只有满足该条件的元素才会被查询出来。
        :return:
        """
        print("==============================any 方法使用案例1=========================================")
        # 用户表（models.User）与 部门表（Dept）为多对多关系
        # 查找出只有满足关联了部门名称为 "人事一部" 的所有用户，没有关联的则不会查询出来
        sql1 = select(models.User).where(models.User.depts.any(models.Dept.name == "人事一部"))
        queryset1 = await self.db.scalars(sql1)
        result1 = queryset1.unique().all()
        for data in result1:
            print(f"用户编号：{data.id} 用户名称：{data.name}")

        print("==============================any 方法使用案例2=========================================")
        # 案例1 取反，查找出只有满足没有关联了部门名称为 "人事一部" 的所有用户，关联的则不会查询出来
        sql2 = select(models.User).where(~models.User.depts.any(models.Dept.name == "人事一部"))
        queryset2 = await self.db.scalars(sql2)
        result2 = queryset2.unique().all()
        for data in result2:
            print(f"用户编号：{data.id} 用户名称：{data.name}")

        print("==============================any 方法使用案例3=========================================")
        # 查询出没有关联部门的所有用户
        sql3 = select(models.User).where(~models.User.depts.any())
        queryset3 = await self.db.scalars(sql3)
        result3 = queryset3.unique().all()
        for data in result3:
            print(f"用户编号：{data.id} 用户名称：{data.name}")

    async def relationship_where_operations_has(self):
        """
        关系运算符操作： has 方法使用示例
        官方文档： https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#relationship-where-operators

        has 方法用于多对一关系中，与 any 方法使用方式同理，只有满足条件的元素才会被查询出来。

        对多关系中使用 has 方法会报错，报错内容如下：
        sqlalchemy.exc.InvalidRequestError: 'has()' not implemented for collections.  Use any().
        :return:
        """
        print("==============================has 方法使用案例1=========================================")
        # 用户（models.User）与 帮助问题（models.Issue）为多对一关系
        # 查找出只有满足关联了用户名称为 "sca-api" 的所有帮助问题，没有关联的则不会查询出来
        sql1 = select(help_models.Issue).where(
            help_models.Issue.create_user.has(models.User.name == "sca-api")
        )
        queryset1 = await self.db.scalars(sql1)
        result1 = queryset1.unique().all()
        for data in result1:
            print(f"问题编号：{data.id} 问题标题：{data.title}")
