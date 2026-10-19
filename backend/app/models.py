from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def utc_now():
    return datetime.now(timezone.utc)


class FoodEntry(Base):
    """One food the user logged, with the calorie estimate and where it came from."""

    __tablename__ = "food_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(64))  # anonymous id from the browser
    # the user's local date, not the server's, so late-night meals land on the right day
    day: Mapped[date] = mapped_column(Date)
    name: Mapped[str] = mapped_column(String(200))
    serving: Mapped[str | None] = mapped_column(String(100))  # e.g. "1 cup cooked"
    grams: Mapped[float | None] = mapped_column(Float)  # estimated portion weight
    calories: Mapped[int] = mapped_column(Integer)  # an estimate, not a measurement
    confidence: Mapped[str] = mapped_column(String(10))  # high, medium or low
    # which usda food the numbers came from, empty when the coach had to guess
    usda_food_id: Mapped[int | None] = mapped_column(Integer)
    usda_description: Mapped[str | None] = mapped_column(String(300))
    source_message: Mapped[str | None] = mapped_column(Text)  # what the user typed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    # every query filters by device and day
    __table_args__ = (Index("ix_food_entries_device_day", "device_id", "day"),)


class ChatMessage(Base):
    """One message in the saved conversation."""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(64), index=True)
    role: Mapped[str] = mapped_column(String(10))  # user or coach
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class UsageCount(Base):
    """Coach calls per device per day, used for the daily limits."""

    __tablename__ = "usage_counts"

    # one row per (device, day). the row with device_id "__global__" counts
    # every device together, for the overall cap
    device_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    day: Mapped[date] = mapped_column(Date, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0)