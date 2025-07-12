from sqlalchemy import select, false
from sqlalchemy.ext.asyncio import AsyncSession

from apps.user import models, schemas
from infra.db.crud import DalBase
from infra.exception.exception import CustomException


class DeptDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(DeptDal, self).__init__(db=db, model=models.Dept, schema=schemas.DeptSimpleOut)

    async def get_tree_list(self, mode: int) -> list:
        """
        1：获取部门树列表
        2：获取部门树选择项，添加/修改部门时使用
        3：获取部门树列表，用户添加部门权限时使用
        :param mode:
        :return:
        """
        if mode == 3:
            sql = select(self.model).where(self.model.disabled == 0, self.model.is_delete == false())
        else:
            sql = select(self.model).where(self.model.is_delete == false())
        queryset = await self.db.scalars(sql)
        datas = list(queryset.all())
        roots = filter(lambda i: not i.parent_id, datas)
        if mode == 1:
            menus = self.generate_tree_list(datas, roots)
        elif mode == 2 or mode == 3:
            menus = self.generate_tree_options(datas, roots)
        else:
            raise CustomException("获取部门失败，无可用选项", code=400)
        return self.dept_order(menus)

    def generate_tree_list(self, depts: list[models.Dept], nodes: filter) -> list:
        """
        生成部门树列表
        :param depts: 总部门列表
        :param nodes: 每层节点部门列表
        :return:
        """
        data = []
        for root in nodes:
            router = schemas.DeptTreeListOut.model_validate(root)
            sons = filter(lambda i: i.parent_id == root.id, depts)
            router.children = self.generate_tree_list(depts, sons)
            data.append(router.model_dump())
        return data

    def generate_tree_options(self, depts: list[models.Dept], nodes: filter) -> list:
        """
        生成部门树选择项
        :param depts: 总部门列表
        :param nodes: 每层节点部门列表
        :return:
        """
        data = []
        for root in nodes:
            router = {"value": root.id, "label": root.name, "order": root.order}
            sons = filter(lambda i: i.parent_id == root.id, depts)
            router["children"] = self.generate_tree_options(depts, sons)
            data.append(router)
        return data

    @classmethod
    def dept_order(cls, datas: list, order: str = "order", children: str = "children") -> list:
        """
        部门排序
        :param datas:
        :param order:
        :param children:
        :return:
        """
        result = sorted(datas, key=lambda dept: dept[order])
        for item in result:
            if item[children]:
                item[children] = sorted(item[children], key=lambda dept: dept[order])
        return result
