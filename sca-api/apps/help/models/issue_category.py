from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from apps.user.models import User
from infra.db.base_model import BaseModel


class IssueCategory(BaseModel):
    __tablename__ = "help_issue_category"
    __table_args__ = ({'comment': '常见问题类别表'})

    name: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="类别名称")
    platform: Mapped[str] = mapped_column(String(8), index=True, nullable=False, comment="展示平台")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否可见")

    issues: Mapped[list["Issue"]] = relationship(back_populates='category')

    create_user_id: Mapped[int] = mapped_column(Integer,ForeignKey("auth_user.id", ondelete='RESTRICT'),comment="创建人")
    create_user: Mapped[User] = relationship(foreign_keys=create_user_id)