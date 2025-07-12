from sqlalchemy.orm import relationship, Mapped, mapped_column
from apps.user.models import User
from infra.db.base_model import BaseModel
from sqlalchemy import String, Boolean, Integer, ForeignKey, Text

class Issue(BaseModel):
    __tablename__ = "help_issue"
    __table_args__ = ({'comment': '常见问题记录表'})

    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False, comment="标题")
    content: Mapped[str] = mapped_column(Text, comment="内容")
    view_number: Mapped[int] = mapped_column(Integer, default=0, comment="查看次数")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否可见")

    category_id: Mapped[int] = mapped_column(Integer,ForeignKey("help_issue_category.id", ondelete='CASCADE'),)
    category: Mapped["IssueCategory"] = relationship(foreign_keys=category_id, back_populates='issues')

    create_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth_user.id", ondelete='RESTRICT'), comment="创建人")
    create_user: Mapped[User] = relationship(foreign_keys=create_user_id)
