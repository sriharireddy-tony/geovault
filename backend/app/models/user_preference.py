import uuid

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class UserPreference(UUIDMixin, Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True,
    )
    theme_mode: Mapped[str] = mapped_column(String(10), default="system")
    theme_color: Mapped[str] = mapped_column(String(20), default="#6366f1")

    user: Mapped["User"] = relationship("User", back_populates="preference")  # noqa: F821
