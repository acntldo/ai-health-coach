from datetime import date

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from .models import ChatMessage, FoodEntry


def get_day_entries(db: Session, device_id: str, day: date) -> list[FoodEntry]:
    query = (
        select(FoodEntry)
        .where(FoodEntry.device_id == device_id, FoodEntry.day == day)
        .order_by(FoodEntry.created_at, FoodEntry.id)
    )
    return list(db.scalars(query))


def get_day_total(db: Session, device_id: str, day: date) -> int:
    total = db.scalar(
        select(func.sum(FoodEntry.calories)).where(
            FoodEntry.device_id == device_id, FoodEntry.day == day
        )
    )
    return total or 0  # sum comes back as None on a day with no entries


def list_day_totals(db: Session, device_id: str) -> list[tuple[date, int]]:
    # newest day first, only days that have entries
    query = (
        select(FoodEntry.day, func.sum(FoodEntry.calories))
        .where(FoodEntry.device_id == device_id)
        .group_by(FoodEntry.day)
        .order_by(FoodEntry.day.desc())
    )
    return [(day, total) for day, total in db.execute(query)]


def get_recent_messages(db: Session, device_id: str, limit: int = 50) -> list[ChatMessage]:
    query = (
        select(ChatMessage)
        .where(ChatMessage.device_id == device_id)
        .order_by(ChatMessage.id.desc())
        .limit(limit)
    )
    return list(reversed(list(db.scalars(query))))  # newest 50, returned oldest first


def delete_entry(db: Session, device_id: str, entry_id: int) -> bool:
    # matching on device_id means a device can only delete its own entries
    result = db.execute(
        delete(FoodEntry).where(FoodEntry.id == entry_id, FoodEntry.device_id == device_id)
    )
    db.commit()
    return result.rowcount > 0