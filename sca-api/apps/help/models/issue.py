from sqlalchemy.orm import relationship, Mapped, mapped_column
from apps.user.models import User
from infra.db.db_base import BaseModel
from sqlalchemy import String, Boolean, Integer, ForeignKey, Text


class IssueCategory(BaseModel):
    __tablename__ = "help_issue_category"
    __table_args__ = ({'comment': '常见问题类别表'})

    name: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="类别名称")
    platform: Mapped[str] = mapped_column(String(8), index=True, nullable=False, comment="展示平台")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否可见")

    issues: Mapped[list["Issue"]] = relationship(back_populates='category')

    create_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("auth_user.id", ondelete='RESTRICT'),
        comment="创建人"
    )
    create_user: Mapped[User] = relationship(foreign_keys=create_user_id)


class Issue(BaseModel):
    __tablename__ = "help_issue"
    __table_args__ = ({'comment': '常见问题记录表'})

    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("help_issue_category.id", ondelete='CASCADE'),
        comment="类别"
    )
    category: Mapped[list["IssueCategory"]] = relationship(foreign_keys=category_id, back_populates='issues')

    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False, comment="标题")
    content: Mapped[str] = mapped_column(Text, comment="内容")
    view_number: Mapped[int] = mapped_column(Integer, default=0, comment="查看次数")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否可见")

    create_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("auth_user.id", ondelete='RESTRICT'),
        comment="创建人"
    )
    create_user: Mapped[User] = relationship(foreign_keys=create_user_id)
