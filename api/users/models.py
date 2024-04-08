from datetime import datetime
import uuid
from core.models.base import Base

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import sqlalchemy as sa


class UserModel(Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(index=True)
    password: Mapped[str]
    fio: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)


class RefreshSessionModel(Base):
    __tablename__ = "refresh_session"

    refresh_token: Mapped[uuid.UUID] = mapped_column(UUID, index=True)
    expires_in: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=func.now()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, sa.ForeignKey("user.id", ondelete="CASCADE")
    )
