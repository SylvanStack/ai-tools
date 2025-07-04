from sqlalchemy.orm import relationship, Mapped, mapped_column
from infra.db.db_base import BaseModel
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer


class DictType(BaseModel):
    __tablename__ = "system_dict_type"
    __table_args__ = ({'comment': '字典类型表'})

    dict_name: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="字典名称")
    dict_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="字典类型")
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, comment="字典状态，是否禁用")
    remark: Mapped[str | None] = mapped_column(String(255), comment="备注")
    details: Mapped[list["DictDetails"]] = relationship(back_populates="dict_type")


class DictDetails(BaseModel):
    __tablename__ = "system_dict_details"
    __table_args__ = ({'comment': '字典详情表'})

    label: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="字典标签")
    value: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="字典键值")
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, comment="字典状态，是否禁用")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否默认")
    order: Mapped[int] = mapped_column(Integer, comment="字典排序")
    dict_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("system_dict_type.id", ondelete='CASCADE'),
        comment="关联字典类型"
    )
    dict_type: Mapped[DictType] = relationship(foreign_keys=dict_type_id, back_populates="details")
    remark: Mapped[str | None] = mapped_column(String(255), comment="备注")
