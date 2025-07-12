import copy
from datetime import datetime
from typing import Any

from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from application import settings
from apps.system import crud as system_crud
from apps.user import models, schemas
from apps.user.params import UserParams
from infra.db.crud import DalBase
from infra.exception.exception import CustomException
from infra.utils import status
from infra.utils.excel.excel_manage import ExcelManage
from infra.utils.excel.import_manage import ImportManage, FieldType
from infra.utils.excel.write_xlsx import WriteXlsx
from infra.utils.file.aliyun_oss import AliyunOSS, BucketConf
from infra.utils.send_email import EmailSender
from infra.utils.sms.reset_passwd import ResetPasswordSMS
from infra.utils.tools import test_password
from infra.utils.validator_utils import vali_telephone
from infra.utils.wx.oauth import WXOAuth
# 修改导入路径，使用完全限定路径
from apps.user.curd.dept_dal import DeptDal
from apps.user.curd.role_dal import RoleDal


class UserDal(DalBase):
    import_headers = [
        {"label": "姓名", "field": "name", "required": True},
        {"label": "昵称", "field": "nickname", "required": False},
        {"label": "手机号", "field": "telephone", "required": True, "rules": [vali_telephone]},
        {"label": "性别", "field": "gender", "required": False},
        {"label": "关联角色", "field": "role_ids", "required": True, "type": FieldType.list},
    ]

    def __init__(self, db: AsyncSession):
        super(UserDal, self).__init__(db=db, model=models.User, schema=schemas.UserSimpleOut)

    async def recursion_get_dept_ids(
            self,
            user: models.User,
            depts: list[models.Dept] = None,
            dept_ids: list[int] = None
    ) -> list:
        """
        递归获取所有关联部门 id
        :param user:
        :param depts: 所有部门实例
        :param dept_ids: 父级部门 id 列表
        :return:
        """
        if not depts:
            depts = await DeptDal(self.db).get_datas(limit=0, v_return_objs=True)
            result = []
            for i in user.depts:
                result.append(i.id)
            result.extend(await self.recursion_get_dept_ids(user, depts, result))
            return list(set(result))
        elif dept_ids:
            result = [i.id for i in filter(lambda item: item.parent_id in dept_ids, depts)]
            result.extend(await self.recursion_get_dept_ids(user, depts, result))
            return result
        else:
            return []

    async def update_login_info(self, user: models.User, last_ip: str) -> None:
        """
        更新当前登录信息
        :param user: 用户对象
        :param last_ip: 最近一次登录 IP
        :return:
        """
        user.last_ip = last_ip
        user.last_login = datetime.now()
        await self.db.flush()

    async def create_data(
            self,
            data: schemas.UserIn,
            v_options: list[_AbstractLoad] = None,
            v_return_obj: bool = False,
            v_schema: Any = None
    ) -> Any:
        """
        创建用户
        :param data:
        :param v_options:
        :param v_return_obj:
        :param v_schema:
        :return:
        """
        unique = await self.get_data(telephone=data.telephone, v_return_none=True)
        if unique:
            raise CustomException("手机号已存在！", code=status.HTTP_ERROR)
        password = data.telephone[5:12] if settings.DEFAULT_PASSWORD == "0" else settings.DEFAULT_PASSWORD
        data.password = self.model.get_password_hash(password)
        data.avatar = data.avatar if data.avatar else settings.DEFAULT_AVATAR
        obj = self.model(**data.model_dump(exclude={'role_ids', "dept_ids"}))
        if data.role_ids:
            roles = await RoleDal(self.db).get_datas(limit=0, id=("in", data.role_ids), v_return_objs=True)
            for role in roles:
                obj.roles.add(role)
        if data.dept_ids:
            depts = await DeptDal(self.db).get_datas(limit=0, id=("in", data.dept_ids), v_return_objs=True)
            for dept in depts:
                obj.depts.add(dept)
        await self.flush(obj)
        return await self.out_dict(obj, v_options, v_return_obj, v_schema)

    async def put_data(
            self,
            data_id: int,
            data: schemas.UserUpdate,
            v_options: list[_AbstractLoad] = None,
            v_return_obj: bool = False,
            v_schema: Any = None
    ) -> Any:
        """
        更新用户信息
        :param data_id:
        :param data:
        :param v_options:
        :param v_return_obj:
        :param v_schema:
        :return:
        """
        obj = await self.get_data(data_id, v_options=[joinedload(self.model.roles), joinedload(self.model.depts)])
        data_dict = jsonable_encoder(data)
        for key, value in data_dict.items():
            if key == "role_ids":
                if value:
                    roles = await RoleDal(self.db).get_datas(limit=0, id=("in", value), v_return_objs=True)
                    if obj.roles:
                        obj.roles.clear()
                    for role in roles:
                        obj.roles.add(role)
                continue
            elif key == "dept_ids":
                if value:
                    depts = await DeptDal(self.db).get_datas(limit=0, id=("in", value), v_return_objs=True)
                    if obj.depts:
                        obj.depts.clear()
                    for dept in depts:
                        obj.depts.add(dept)
                continue
            setattr(obj, key, value)
        await self.flush(obj)
        return await self.out_dict(obj, None, v_return_obj, v_schema)

    async def reset_current_password(self, user: models.User, data: schemas.ResetPwd) -> None:
        """
        重置密码
        :param user:
        :param data:
        :return:
        """
        if data.password != data.password_two:
            raise CustomException(msg="两次密码不一致", code=400)
        result = test_password(data.password)
        if isinstance(result, str):
            raise CustomException(msg=result, code=400)
        user.password = self.model.get_password_hash(data.password)
        user.is_reset_password = True
        await self.flush(user)

    async def update_current_info(self, user: models.User, data: schemas.UserUpdateBaseInfo) -> Any:
        """
        更新当前用户基本信息
        :param user:
        :param data:
        :return:
        """
        if data.telephone != user.telephone:
            unique = await self.get_data(telephone=data.telephone, v_return_none=True)
            if unique:
                raise CustomException("手机号已存在！", code=status.HTTP_ERROR)
            else:
                user.telephone = data.telephone
        user.name = data.name
        user.nickname = data.nickname
        user.gender = data.gender
        await self.flush(user)
        return await self.out_dict(user)

    async def export_query_list(self, header: list, params: UserParams) -> dict:
        """
        导出用户查询列表为 excel
        :param header:
        :param params:
        :return:
        """
        datas = await self.get_datas(
            **params.dict(),
            v_return_objs=True,
            v_options=[joinedload(self.model.depts), joinedload(self.model.roles)]
        )
        # 获取表头
        row = list(map(lambda i: i.get("label"), header))
        rows = []
        options = await self.get_export_headers_options()
        for user in datas:
            data = []
            for item in header:
                field = item.get("field")
                # 通过反射获取对应的属性值
                value = getattr(user, field, "")
                if field == "is_active":
                    value = "可用" if value else "停用"
                elif field == "is_staff":
                    value = "是" if value else "否"
                elif field == "gender":
                    result = list(filter(lambda i: i["value"] == value, options["gender_options"]))
                    value = result[0]["label"] if result else ""
                elif field == "roles":
                    value = ",".join([i.name for i in value])
                elif field == "depts":
                    value = ",".join([i.name for i in value])
                data.append(value)
            rows.append(data)
        em = ExcelManage()
        em.create_excel("用户列表")
        em.write_list(rows, row)
        remote_file_url = em.save_excel().get("remote_path")
        em.close()
        return {"url": remote_file_url, "filename": "用户列表.xlsx"}

    async def get_export_headers_options(self, include: list[str] = None) -> dict[str, list]:
        """
        获取导出所需选择项
        :param include: 包括的选择项
        :return:
        """
        options = {}
        # 性别选择项
        if include is None or 'gender' in include:
            gender_objs = await system_crud.DictTypeDal(self.db).get_dicts_details(["sys__gender"])
            sys__gender = gender_objs.get("sys__gender", [])
            gender_options = [{"label": i["label"], "value": i["value"]} for i in sys__gender]
            options["gender_options"] = gender_options
        return options

    async def get_import_headers_options(self) -> None:
        """
        补全表头数据选项
        :return:
        """
        # 角色选择项
        role_options = await RoleDal(self.db).get_datas(limit=0, v_return_objs=True, disabled=False, is_admin=False)
        role_item = self.import_headers[4]
        assert isinstance(role_item, dict)
        role_item["options"] = [{"label": role.name, "value": role.id} for role in role_options]

        # 性别选择项
        gender_options = await system_crud.DictTypeDal(self.db).get_dicts_details(["sys__gender"])
        gender_item = self.import_headers[3]
        assert isinstance(gender_item, dict)
        sys__gender = gender_options.get("sys__gender")
        gender_item["options"] = [{"label": item["label"], "value": item["value"]} for item in sys__gender]

    async def download_import_template(self) -> dict:
        """
        下载用户最新版导入模板
        :return:
        """
        await self.get_import_headers_options()
        em = WriteXlsx()
        em.create_excel(sheet_name="用户导入模板", save_static=True)
        em.generate_template(copy.deepcopy(self.import_headers))
        em.close()
        return {"url": em.get_file_url(), "filename": "用户导入模板.xlsx"}

    async def import_users(self, file: UploadFile) -> dict:
        """
        批量导入用户数据
        :param file:
        :return:
        """
        await self.get_import_headers_options()
        im = ImportManage(file, copy.deepcopy(self.import_headers))
        await im.get_table_data()
        im.check_table_data()
        for item in im.success:
            old_data_list = item.pop("old_data_list")
            data = schemas.UserIn(**item)
            try:
                await self.create_data(data)
            except ValueError as e:
                old_data_list.append(e.__str__())
                im.add_error_data(old_data_list)
            except Exception:
                old_data_list.append("创建失败，请联系管理员！")
                im.add_error_data(old_data_list)
        return {
            "success_number": im.success_number,
            "error_number": im.error_number,
            "error_url": im.generate_error_url()
        }

    async def init_password(self, ids: list[int]) -> list:
        """
        初始化所选用户密码
        将用户密码改为系统默认密码，并将初始化密码状态改为false
        :param ids:
        :return:
        """
        users = await self.get_datas(limit=0, id=("in", ids), v_return_objs=True)
        result = []
        for user in users:
            # 重置密码
            data = {"id": user.id, "telephone": user.telephone, "name": user.name, "email": user.email}
            password = user.telephone[5:12] if settings.DEFAULT_PASSWORD == "0" else settings.DEFAULT_PASSWORD
            user.password = self.model.get_password_hash(password)
            user.is_reset_password = False
            self.db.add(user)
            data["reset_password_status"] = True
            data["password"] = password
            result.append(data)
        await self.db.flush()
        return result

    async def init_password_send_sms(self, ids: list[int], rd: Redis) -> list:
        """
        初始化所选用户密码并发送通知短信
        将用户密码改为系统默认密码，并将初始化密码状态改为false
        :param ids:
        :param rd:
        :return:
        """
        result = await self.init_password(ids)
        for user in result:
            if not user["reset_password_status"]:
                user["send_sms_status"] = False
                user["send_sms_msg"] = "重置密码失败"
                continue
            password = user.pop("password")
            sms = ResetPasswordSMS([user.get("telephone")], rd)
            try:
                send_result = (await sms.main_async(password=password))[0]
                user["send_sms_status"] = send_result
                user["send_sms_msg"] = "" if send_result else "短信发送失败，请联系管理员"
            except CustomException as e:
                user["send_sms_status"] = False
                user["send_sms_msg"] = e.msg
        return result

    async def init_password_send_email(self, ids: list[int], rd: Redis) -> list:
        """
        初始化所选用户密码并发送通知邮件
        将用户密码改为系统默认密码，并将初始化密码状态改为false
        :param ids:
        :param rd:
        :return:
        """
        result = await self.init_password(ids)
        for user in result:
            if not user["reset_password_status"]:
                user["send_sms_status"] = False
                user["send_sms_msg"] = "重置密码失败"
                continue
            password: str = user.pop("password")
            email: str = user.get("email", None)
            if email:
                subject = "密码已重置"
                body = f"您好，您的密码已经重置为{password}，请及时登录并修改密码。"
                es = EmailSender(rd)
                try:
                    send_result = await es.send_email([email], subject, body)
                    user["send_sms_status"] = send_result
                    user["send_sms_msg"] = "" if send_result else "短信发送失败，请联系管理员"
                except CustomException as e:
                    user["send_sms_status"] = False
                    user["send_sms_msg"] = e.msg
            else:
                user["send_sms_status"] = False
                user["send_sms_msg"] = "未获取到邮箱地址"
        return result

    async def update_current_avatar(self, user: models.User, file: UploadFile) -> str:
        """
        更新当前用户头像
        :param user:
        :param file:
        :return:
        """
        result = await AliyunOSS(BucketConf(**settings.ALIYUN_OSS)).upload_image("avatar", file)
        user.avatar = result
        await self.flush(user)
        return result

    async def update_wx_server_openid(self, code: str, user: models.User, redis: Redis) -> bool:
        """
        更新用户服务端微信平台openid
        :param code:
        :param user:
        :param redis:
        :return:
        """
        wx = WXOAuth(redis, 0)
        openid = await wx.parsing_openid(code)
        if not openid:
            return False
        user.is_wx_server_openid = True
        user.wx_server_openid = openid
        await self.flush(user)
        return True

    async def delete_datas(self, ids: list[int], v_soft: bool = False, **kwargs) -> None:
        """
        删除多个用户，软删除
        删除后清空所关联的角色
        :param ids: 数据集
        :param v_soft: 是否执行软删除
        :param kwargs: 其他更新字段
        """
        options = [joinedload(self.model.roles)]
        objs = await self.get_datas(limit=0, id=("in", ids), v_options=options, v_return_objs=True)
        for obj in objs:
            if obj.roles:
                obj.roles.clear()
        return await super(UserDal, self).delete_datas(ids, v_soft, **kwargs)