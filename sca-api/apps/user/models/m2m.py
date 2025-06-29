from infra.db.db_base import BaseModel
from infra.db.db_base import Base
from sqlalchemy import ForeignKey, Column, Table, Integer

auth_user_roles = Table(
    "auth_user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("auth_user.id", ondelete="CASCADE")),
    Column("role_id", Integer, ForeignKey("auth_role.id", ondelete="CASCADE")),
)

auth_role_menus = Table(
    "auth_role_menus",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("auth_role.id", ondelete="CASCADE")),
    Column("menu_id", Integer, ForeignKey("auth_menu.id", ondelete="CASCADE")),
)

auth_user_depts = Table(
    "auth_user_depts",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("auth_user.id", ondelete="CASCADE")),
    Column("dept_id", Integer, ForeignKey("auth_dept.id", ondelete="CASCADE")),
)

auth_role_depts = Table(
    "auth_role_depts",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("auth_role.id", ondelete="CASCADE")),
    Column("dept_id", Integer, ForeignKey("auth_dept.id", ondelete="CASCADE")),
)
