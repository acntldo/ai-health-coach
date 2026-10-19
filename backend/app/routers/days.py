from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..deps import get_device_id
from ..schemas import DaySummary, DayTotal, FoodEntryOut

router = APIRouter(prefix="/api/days", tags=["days"])


@router.get("", response_model=list[DayTotal])
def list_days(device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    return [DayTotal(day=d, total=t) for d, t in crud.list_day_totals(db, device_id)]


@router.get("/{day}", response_model=DaySummary)
def read_day(
    day: date,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    # a day with no food returns a total of 0 instead of a 404
    entries = crud.get_day_entries(db, device_id, day)
    return DaySummary(
        day=day,
        total=sum(e.calories for e in entries),
        entries=[FoodEntryOut.model_validate(e) for e in entries],
    )