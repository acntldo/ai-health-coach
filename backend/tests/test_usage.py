from datetime import date

import pytest

from app.models import UsageCount
from app.usage import GLOBAL_ID, LimitReached, consume

DAY = date(2026, 10, 21)


def count_for(session_factory, device_id, day=DAY):
    # fresh session so the number comes from the database, not a cached object
    with session_factory() as db:
        row = db.get(UsageCount, (device_id, day))
        return row.count if row else 0


def test_device_limit_blocks_the_next_call(session_factory):
    with session_factory() as db:
        consume(db, "device-aaaa", DAY, device_limit=2, global_limit=100)
        consume(db, "device-aaaa", DAY, device_limit=2, global_limit=100)
        with pytest.raises(LimitReached) as exc:
            consume(db, "device-aaaa", DAY, device_limit=2, global_limit=100)
    assert exc.value.scope == "device"


def test_global_limit_counts_all_devices_together(session_factory):
    with session_factory() as db:
        consume(db, "device-aaaa", DAY, device_limit=5, global_limit=2)
        consume(db, "device-bbbb", DAY, device_limit=5, global_limit=2)
        with pytest.raises(LimitReached) as exc:
            consume(db, "device-cccc", DAY, device_limit=5, global_limit=2)
    assert exc.value.scope == "global"


def test_blocked_device_does_not_use_up_the_global_count(session_factory):
    with session_factory() as db:
        consume(db, "device-aaaa", DAY, device_limit=1, global_limit=10)
        with pytest.raises(LimitReached):
            consume(db, "device-aaaa", DAY, device_limit=1, global_limit=10)
    assert count_for(session_factory, GLOBAL_ID) == 1
    assert count_for(session_factory, "device-aaaa") == 1


def test_limits_reset_on_a_new_day(session_factory):
    with session_factory() as db:
        consume(db, "device-aaaa", DAY, device_limit=1, global_limit=10)
        consume(db, "device-aaaa", date(2026, 10, 22), device_limit=1, global_limit=10)