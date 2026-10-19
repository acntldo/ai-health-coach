from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class FoodEntryOut(BaseModel):
    # lets a database row be returned as is
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    serving: str | None
    grams: float | None
    calories: int
    confidence: Literal["high", "medium", "low"]
    usda_description: str | None


class DayTotal(BaseModel):
    day: date
    total: int


class DaySummary(BaseModel):
    day: date
    total: int
    entries: list[FoodEntryOut]


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: Literal["user", "coach"]
    text: str
    created_at: datetime