from core.models.base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import JSON, LargeBinary
from sqlalchemy.sql import func


class DataSets(Base):

    dataset_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    dataset: Mapped[dict | list | str] = mapped_column(type_=JSON, nullable=False)


class TrainedModels(Base):

    name_model: Mapped[str] = mapped_column(nullable=False, unique=True)
    type_model: Mapped[str] = mapped_column(nullable=False)
    data_model: Mapped[bytes] = mapped_column(type_=LargeBinary, nullable=False)
