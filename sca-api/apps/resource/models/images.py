from sqlalchemy.orm import relationship, Mapped, mapped_column
from apps.user.models import User
from infra.db.base_model import BaseModel
from sqlalchemy import String, ForeignKey, Integer


class Images(BaseModel):
    __tablename__ = "resource_images"
    __table_args__ = ({'comment': '图片素材表'})

    filename: Mapped[str] = mapped_column(String(255), nullable=False, comment="原图片名称")
    image_url: Mapped[str] = mapped_column(String(500), nullable=False, comment="图片链接")

    create_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("auth_user.id", ondelete='RESTRICT'),
        comment="创建人"
    )
    create_user: Mapped[User] = relationship(foreign_keys=create_user_id)
