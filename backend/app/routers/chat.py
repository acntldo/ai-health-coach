import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud
from ..coach import run_coach
from ..config import DEVICE_DAILY_LIMIT
from ..database import get_db
from ..deps import get_device_id
from ..gemini import GeminiError
from ..models import ChatMessage, FoodEntry
from ..schemas import ChatRequest, ChatResponse, FoodEntryOut
from ..usage import LimitReached, consume
from ..usda import UsdaError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

HISTORY_TURNS = 10  # recent messages the coach can see


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    today_utc = datetime.now(timezone.utc).date()
    # a local date is at most a day away from the utc date, whatever the time zone
    if abs((payload.day - today_utc).days) > 1:
        raise HTTPException(status_code=422, detail="The date must be today's date.")

    # counted before the coach runs, a failed attempt still uses up quota
    try:
        consume(db, device_id, today_utc)
    except LimitReached as limit:
        if limit.scope == "device":
            detail = f"You've reached today's limit of {DEVICE_DAILY_LIMIT} messages. It resets at midnight UTC."
        else:
            detail = "The coach has reached its daily limit for all users. Please try again tomorrow (it resets at midnight UTC)."
        raise HTTPException(status_code=429, detail=detail)

    history = [(m.role, m.text) for m in crud.get_recent_messages(db, device_id, HISTORY_TURNS)]
    day_entries = [(e.name, e.calories) for e in crud.get_day_entries(db, device_id, payload.day)]

    try:
        result = run_coach(payload.message, history, day_entries)
    except (GeminiError, UsdaError) as exc:
        # the real cause stays in the log, visitors only get a generic message
        logger.warning("coach failed: %s", exc)
        raise HTTPException(
            status_code=503, detail="The coach is unavailable right now. Please try again in a minute."
        )

    # saved only after the coach succeeded, so a failure leaves no half-finished chat
    db.add(ChatMessage(device_id=device_id, role="user", text=payload.message))
    db.add(ChatMessage(device_id=device_id, role="coach", text=result.reply))
    entries = [
        FoodEntry(
            device_id=device_id,
            day=payload.day,
            name=item.name,
            serving=item.serving,
            grams=item.grams,
            calories=item.calories,
            confidence=item.confidence,
            usda_food_id=item.usda_food_id,
            usda_description=item.usda_description,
            source_message=payload.message,
        )
        for item in result.items
    ]
    db.add_all(entries)
    db.commit()

    return ChatResponse(
        reply=result.reply,
        entries=[FoodEntryOut.model_validate(e) for e in entries],
        day_total=crud.get_day_total(db, device_id, payload.day),
    )