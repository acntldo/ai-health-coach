from datetime import date

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import DEVICE_DAILY_LIMIT, GLOBAL_DAILY_LIMIT
from .models import UsageCount

# real device ids can't contain underscores, so this never matches one
GLOBAL_ID = "__global__"


class LimitReached(Exception):
    def __init__(self, scope: str):
        super().__init__(scope)
        self.scope = scope  # "device" or "global"


def _ensure_row(db: Session, device_id: str, day: date) -> None:
    if db.get(UsageCount, (device_id, day)) is None:
        try:
            db.add(UsageCount(device_id=device_id, day=day, count=0))
            db.commit()
        except IntegrityError:
            db.rollback()  # another request created the row first


def _increment(db: Session, device_id: str, day: date, limit: int) -> bool:
    # a single conditional update, so two simultaneous requests can't both pass the limit
    result = db.execute(
        update(UsageCount)
        .where(UsageCount.device_id == device_id, UsageCount.day == day, UsageCount.count < limit)
        .values(count=UsageCount.count + 1)
    )
    return result.rowcount == 1


def consume(
    db: Session,
    device_id: str,
    day: date,
    device_limit: int = DEVICE_DAILY_LIMIT,
    global_limit: int = GLOBAL_DAILY_LIMIT,
) -> None:
    """Counts one coach call, or raises LimitReached. Called before the coach runs."""
    for row_id in (device_id, GLOBAL_ID):
        _ensure_row(db, row_id, day)

    if not _increment(db, GLOBAL_ID, day, global_limit):
        db.rollback()
        raise LimitReached("global")
    if not _increment(db, device_id, day, device_limit):
        # rolling back also undoes the overall count, a blocked device shouldn't use it up
        db.rollback()
        raise LimitReached("device")
    db.commit()