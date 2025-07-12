from sqlalchemy import select, false
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.user import models, schemas
from infra.db.crud import DalBase
from infra.exception.exception import CustomException
# 移除此处的导入，改为在方法内部导入
# from .role_dal import RoleDal
from .user_dal import UserDal


class MenuDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(MenuDal, self).__init__(db=db, model=models.Menu, schema=schemas.MenuSimpleOut)

    async def get_tree_list(self, mode: int) -> list:
        """
        1：获取菜单树列表
        2：获取菜单树选择项，添加/修改菜单时使用
        3：获取菜单树列表，角色添加菜单权限时使用
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
            raise CustomException("获取菜单失败，无可用选项", code=400)
        return self.menus_order(menus)

    async def get_routers(self, user: models.User) -> list:
        """
        获取路由表
        declare interface AppCustomRouteRecordRaw extends Omit<RouteRecordRaw, 'meta'> {
            name: string
            meta: RouteMeta
            component: string
            path: string
            redirect: string
            children?: AppCustomRouteRecordRaw[]
        }
        :param user:
        :return:
        """
        if any([i.is_admin for i in user.roles]):
            sql = select(self.model) \
                .where(self.model.disabled == 0, self.model.menu_type != "2", self.model.is_delete == false())
            queryset = await self.db.scalars(sql)
            datas = list(queryset.all())
        else:
            options = [joinedload(models.User.roles).subqueryload(models.Role.menus)]
            user = await UserDal(self.db).get_data(user.id, v_options=options)
            datas = set()
            for role in user.roles:
                for menu in role.menus:
                    # 该路由没有被禁用，并且菜单不是按钮
                    if not menu.disabled and menu.menu_type != "2":
                        datas.add(menu)
        roots = filter(lambda i: not i.parent_id, datas)
        menus = self.generate_router_tree(datas, roots)
        return self.menus_order(menus)

    def generate_router_tree(self, menus: list[models.Menu], nodes: filter, name: str = "") -> list:
        """
        生成路由树
        :param menus: 总菜单列表
        :param nodes: 节点菜单列表
        :param name: name拼接，切记Name不能重复
        :return:
        """
        data = []
        for root in nodes:
            router = schemas.RouterOut.model_validate(root)
            router.name = name + "".join(name.capitalize() for name in router.path.split("/"))
            router.meta = schemas.Meta(
                title=root.title,
                icon=root.icon,
                hidden=root.hidden,
                alwaysShow=root.alwaysShow,
                noCache=root.noCache
            )
            if root.menu_type == "0":
                sons = filter(lambda i: i.parent_id == root.id, menus)
                router.children = self.generate_router_tree(menus, sons, router.name)
            data.append(router.model_dump())
        return data

    def generate_tree_list(self, menus: list[models.Menu], nodes: filter) -> list:
        """
        生成菜单树列表
        :param menus: 总菜单列表
        :param nodes: 每层节点菜单列表
        :return:
        """
        data = []
        for root in nodes:
            router = schemas.MenuTreeListOut.model_validate(root)
            if root.menu_type == "0" or root.menu_type == "1":
                sons = filter(lambda i: i.parent_id == root.id, menus)
                router.children = self.generate_tree_list(menus, sons)
            data.append(router.model_dump())
        return data

    def generate_tree_options(self, menus: list[models.Menu], nodes: filter) -> list:
        """
        生成菜单树选择项
        :param menus:总菜单列表
        :param nodes:每层节点菜单列表
        :return:
        """
        data = []
        for root in nodes:
            router = {"value": root.id, "label": root.title, "order": root.order}
            if root.menu_type == "0" or root.menu_type == "1":
                sons = filter(lambda i: i.parent_id == root.id, menus)
                router["children"] = self.generate_tree_options(menus, sons)
            data.append(router)
        return data

    @classmethod
    def menus_order(cls, datas: list, order: str = "order", children: str = "children") -> list:
        """
        菜单排序
        :param datas:
        :param order:
        :param children:
        :return:
        """
        result = sorted(datas, key=lambda menu: menu[order])
        for item in result:
            if item[children]:
                item[children] = sorted(item[children], key=lambda menu: menu[order])
        return result

    async def delete_datas(self, ids: list[int], v_soft: bool = False, **kwargs) -> None:
        """
        删除多个菜单
        如果存在角色关联则无法删除
        :param ids: 数据集
        :param v_soft: 是否执行软删除
        :param kwargs: 其他更新字段
        :return:
        """
        # 在方法内部导入RoleDal
        from .role_dal import RoleDal
        
        count = await RoleDal(self.db).get_count(v_join=[["menus"]], v_where=[self.model.id.in_(ids)])
        if count > 0:
            raise CustomException("无法删除存在角色关联的菜单", code=400)
        await super(MenuDal, self).delete_datas(ids, v_soft, **kwargs)
