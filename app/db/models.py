from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    plan_tier: Mapped[str] = mapped_column(String(32), nullable=False, default="free")
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
    )

    usage_logs: Mapped[list["UsageLog"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    stimuli: Mapped[list["Stimulus"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    admin_notifications: Mapped[list["AdminNotification"]] = relationship(
        back_populates="reporting_user",
        cascade="all, delete-orphan",
    )


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped[User] = relationship(back_populates="usage_logs")


class Stimulus(Base):
    __tablename__ = "stimuli"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(String(500), nullable=False)
    insight: Mapped[str] = mapped_column(String(2000), nullable=False)
    source_text: Mapped[str] = mapped_column(String(10000), nullable=False)
    flagged_for_review: Mapped[bool] = mapped_column(nullable=False, default=False)
    report_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    flagged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="stimuli")
    admin_notifications: Mapped[list["AdminNotification"]] = relationship(
        back_populates="stimulus",
        cascade="all, delete-orphan",
    )


class AdminNotification(Base):
    __tablename__ = "admin_notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    stimulus_id: Mapped[int] = mapped_column(ForeignKey("stimuli.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    is_read: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    reporting_user: Mapped[User] = relationship(back_populates="admin_notifications")
    stimulus: Mapped[Stimulus] = relationship(back_populates="admin_notifications")
