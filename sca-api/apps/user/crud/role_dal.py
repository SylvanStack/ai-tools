from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from apps.user import models, schemas
from infra.db.crud import DalBase
from infra.exception.exception import CustomException
# 移除此处的导入，改为在方法内部导入
# from .menu_dal import MenuDal
from .dept_dal import DeptDal
# 移除此处的导入，改为在方法内部导入
# from .user_dal import UserDal


class RoleDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(RoleDal, self).__init__(db=db, model=models.Role, schema=schemas.RoleSimpleOut)

    async def create_data(
            self,
            data: schemas.RoleIn,
            v_options: list[_AbstractLoad] = None,
            v_return_obj: bool = False,
            v_schema: Any = None
    ) -> Any:
        """
        创建数据
        :param data:
        :param v_options:
        :param v_return_obj:
        :param v_schema:
        :return:
        """
        # 在方法内部导入MenuDal
        from .menu_dal import MenuDal
        
        obj = self.model(**data.model_dump(exclude={'menu_ids', 'dept_ids'}))
        if data.menu_ids:
            menus = await MenuDal(db=self.db).get_datas(limit=0, id=("in", data.menu_ids), v_return_objs=True)
            for menu in menus:
                obj.menus.add(menu)
        if data.dept_ids:
            depts = await DeptDal(db=self.db).get_datas(limit=0, id=("in", data.dept_ids), v_return_objs=True)
            for dept in depts:
                obj.depts.add(dept)
        await self.flush(obj)
        return await self.out_dict(obj, v_options, v_return_obj, v_schema)

    async def put_data(
            self,
            data_id: int,
            data: schemas.RoleIn,
            v_options: list[_AbstractLoad] = None,
            v_return_obj: bool = False,
            v_schema: Any = None
    ) -> Any:
        """
        更新单个数据
        :param data_id:
        :param data:
        :param v_options:
        :param v_return_obj:
        :param v_schema:
        :return:
        """
        # 在方法内部导入MenuDal
        from .menu_dal import MenuDal
        
        obj = await self.get_data(data_id, v_options=[joinedload(self.model.menus), joinedload(self.model.depts)])
        obj_dict = jsonable_encoder(data)
        for key, value in obj_dict.items():
            if key == "menu_ids":
                if value:
                    menus = await MenuDal(db=self.db).get_datas(limit=0, id=("in", value), v_return_objs=True)
                    if obj.menus:
                        obj.menus.clear()
                    for menu in menus:
                        obj.menus.add(menu)
                continue
            elif key == "dept_ids":
                if value:
                    depts = await DeptDal(db=self.db).get_datas(limit=0, id=("in", value), v_return_objs=True)
                    if obj.depts:
                        obj.depts.clear()
                    for dept in depts:
                        obj.depts.add(dept)
                continue
            setattr(obj, key, value)
        await self.flush(obj)
        return await self.out_dict(obj, None, v_return_obj, v_schema)

    async def get_role_menu_tree(self, role_id: int) -> list:
        role = await self.get_data(role_id, v_options=[joinedload(self.model.menus)])
        return [i.id for i in role.menus]

    async def get_select_datas(self) -> list:
        """
        获取选择数据，全部数据
        :return:
        """
        sql = select(self.model)
        queryset = await self.db.scalars(sql)
        return [schemas.RoleOptionsOut.model_validate(i).model_dump() for i in queryset.all()]

    async def delete_datas(self, ids: list[int], v_soft: bool = False, **kwargs) -> None:
        """
        删除多个角色，硬删除
        如果存在用户关联则无法删除
        :param ids: 数据集
        :param v_soft: 是否执行软删除
        :param kwargs: 其他更新字段
        """
        # 在方法内部导入UserDal
        from .user_dal import UserDal
        
        user_count = await UserDal(self.db).get_count(v_join=[["roles"]], v_where=[models.Role.id.in_(ids)])
        if user_count > 0:
            raise CustomException("无法删除存在用户关联的角色", code=400)
        return await super(RoleDal, self).delete_datas(ids, v_soft, **kwargs)

