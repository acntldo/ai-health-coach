from typing import Literal

from pydantic import BaseModel

from .gemini import generate_json
from .prompts import DECIDE_PROMPT, UNDERSTAND_PROMPT
from .usda import FoodMatch, search_foods

MAX_FOODS = 8  # per message, keeps usda lookups and the prompt small
# sanity limits on what the model returns, fat is about 900 kcal per 100 g
MAX_KCAL_PER_100G = 900
MIN_GRAMS, MAX_GRAMS = 1, 3000
MAX_ITEM_KCAL = 5000


class FoodRequest(BaseModel):
    search: str
    amount: str | None = None


class Understanding(BaseModel):
    language: str = "English"  # language of the user's message, passed to the second call
    reply: str
    foods: list[FoodRequest] = []


class ChosenItem(BaseModel):
    food_index: int
    fdc_id: int | None = None
    name: str
    serving: str | None = None
    grams: float
    kcal_per_100g: float
    confidence: Literal["high", "medium", "low"]


class Decision(BaseModel):
    reply: str
    items: list[ChosenItem] = []


class LoggedItem(BaseModel):
    """A food ready to save, with the calories already worked out."""

    name: str
    serving: str | None
    grams: float
    calories: int
    confidence: Literal["high", "medium", "low"]
    usda_food_id: int | None
    usda_description: str | None


class CoachResult(BaseModel):
    reply: str
    items: list[LoggedItem] = []


def _understand_prompt(day_entries: list[tuple[str, int]]) -> str:
    if day_entries:
        log = ", ".join(f"{name} ({kcal} kcal)" for name, kcal in day_entries)
        total = sum(kcal for _, kcal in day_entries)
        status = f"Today's log so far: {log}. Total so far: {total} kcal."
    else:
        status = "Nothing has been logged yet today."
    # the total is added up here so the model never has to do the arithmetic
    return f"{UNDERSTAND_PROMPT}\n{status}"


def _decide_message(
    message: str, language: str, foods: list[FoodRequest], candidates: list[list[FoodMatch]]
) -> str:
    lines = [f'The user wrote: "{message}"', f"Reply language: {language}", "", "Foods to match:"]
    for i, (food, matches) in enumerate(zip(foods, candidates)):
        lines.append(f'{i}. searched "{food.search}", amount: {food.amount or "not stated"}')
        if not matches:
            lines.append("   - no USDA matches found")
        for m in matches:
            lines.append(f"   - id {m.fdc_id}: {m.description} ({m.kcal_per_100g:g} kcal per 100 g)")
    return "\n".join(lines)


def _to_logged_item(item: ChosenItem, matches: list[FoodMatch], fallback_name: str) -> LoggedItem | None:
    """Turns the model's pick into a saveable item, or None if the numbers don't hold up."""
    # an id the model made up won't be in the list, and counts as no match
    match = next((m for m in matches if item.fdc_id and m.fdc_id == item.fdc_id), None)
    if match:
        kcal_per_100g = match.kcal_per_100g  # usda's number wins over the model's
        confidence = item.confidence
    else:
        kcal_per_100g = item.kcal_per_100g
        confidence = "low"  # without a usda match the number is a guess

    if not (0 <= kcal_per_100g <= MAX_KCAL_PER_100G and MIN_GRAMS <= item.grams <= MAX_GRAMS):
        return None
    calories = round(kcal_per_100g * item.grams / 100)
    if calories > MAX_ITEM_KCAL:
        return None

    return LoggedItem(
        name=item.name.strip()[:200] or fallback_name,
        serving=item.serving[:100] if item.serving else None,
        grams=item.grams,
        calories=calories,
        confidence=confidence,
        usda_food_id=match.fdc_id if match else None,
        usda_description=match.description if match else None,
    )


def run_coach(
    message: str, history: list[tuple[str, str]], day_entries: list[tuple[str, int]]
) -> CoachResult:
    """history: (role, text) pairs, oldest first, without the new message.
    day_entries: (name, calories) pairs already logged today."""
    turns = [*history, ("user", message)]
    understood = generate_json(_understand_prompt(day_entries), turns, Understanding)

    foods = understood.foods[:MAX_FOODS]
    if not foods:
        reply = understood.reply.strip() or "Tell me what you ate and I'll estimate the calories."
        return CoachResult(reply=reply)

    candidates = [search_foods(f.search) for f in foods]
    decision = generate_json(
        DECIDE_PROMPT,
        [("user", _decide_message(message, understood.language, foods, candidates))],
        Decision,
    )

    items, skipped, answered = [], [], set()
    for item in decision.items:
        if not 0 <= item.food_index < len(foods) or item.food_index in answered:
            continue
        answered.add(item.food_index)
        food = foods[item.food_index]
        logged = _to_logged_item(item, candidates[item.food_index], food.search)
        if logged:
            items.append(logged)
        else:
            skipped.append(food.search)
    # foods the model never answered for are reported too
    skipped += [f.search for i, f in enumerate(foods) if i not in answered]

    if not items:
        return CoachResult(
            reply="I couldn't work out the calories for that. Could you tell me a bit more about what you had?"
        )
    reply = decision.reply.strip()
    if skipped:
        reply += f" I couldn't log: {', '.join(skipped)}."
    return CoachResult(reply=reply, items=items)