from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints


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



class ChatRequest(BaseModel):
    # whitespace is trimmed first, so a message of only spaces is rejected
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    day: date  # the user's local date, sent by the browser


class ChatResponse(BaseModel):
    reply: str
    entries: list[FoodEntryOut]  # the foods this message logged
    day_total: int