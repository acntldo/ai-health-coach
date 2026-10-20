import logging
import time

import httpx
from pydantic import BaseModel, ValidationError

from .config import GEMINI_API_KEY, GEMINI_MODELS

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
OVERLOAD_STATUSES = {500, 502, 503, 504}
ATTEMPTS_PER_MODEL = 2

logger = logging.getLogger(__name__)


class GeminiError(Exception):
    """The model couldn't give a usable answer (no key, network, quota, bad output)."""


def _build_contents(turns: list[tuple[str, str]]) -> list[dict]:
    # gemini needs the chat to start with the user and alternate roles,
    # so a leading coach message is dropped and same-role neighbours are merged
    contents = []
    for role, text in turns:
        role = "user" if role == "user" else "model"
        if not contents and role == "model":
            continue
        if contents and contents[-1]["role"] == role:
            contents[-1]["parts"][0]["text"] += "\n" + text
        else:
            contents.append({"role": role, "parts": [{"text": text}]})
    return contents


def _extract_text(resp: httpx.Response) -> str:
    try:
        resp.raise_for_status()
        parts = resp.json()["candidates"][0]["content"]["parts"]
        # thinking parts are skipped, only the answer text is wanted
        text = "".join(p["text"] for p in parts if "text" in p and not p.get("thought"))
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise GeminiError("The coach is unavailable right now") from exc
    if not text:
        raise GeminiError("The coach is unavailable right now")
    return text


def _call(system_prompt: str, contents: list[dict]) -> str:
    if not GEMINI_API_KEY or not GEMINI_MODELS:
        raise GeminiError("GEMINI_API_KEY and GEMINI_MODELS must be set")

    body = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {"responseMimeType": "application/json"},
    }
    for model in GEMINI_MODELS:
        for attempt in range(1, ATTEMPTS_PER_MODEL + 1):
            try:
                # the key goes in a header so it never shows up in a logged url
                resp = httpx.post(
                    f"{BASE_URL}/{model}:generateContent",
                    headers={"x-goog-api-key": GEMINI_API_KEY},
                    json=body,
                    timeout=20,
                )
            except httpx.HTTPError as exc:
                raise GeminiError("The coach is unavailable right now") from exc

            if resp.status_code in (404, 429):
                # retired or misspelled name, or this model's quota is used up.
                # quotas are per model, so the next one may still have room
                break
            if resp.status_code in OVERLOAD_STATUSES:
                if attempt < ATTEMPTS_PER_MODEL:
                    time.sleep(1)  # overload errors from google are usually brief
                continue
            return _extract_text(resp)
        logger.warning("%s is overloaded or unavailable, trying the next model", model)

    raise GeminiError("The coach is unavailable right now, try again in a minute")


def generate_json(
    system_prompt: str, turns: list[tuple[str, str]], model_cls: type[BaseModel]
) -> BaseModel:
    """Asks gemini for json and checks it against model_cls.

    turns is a list of (role, text) with role "user" or "coach", ending with
    the newest user message."""
    contents = _build_contents(turns)
    for _ in range(2):
        text = _call(system_prompt, contents)
        try:
            return model_cls.model_validate_json(text)
        except ValidationError:
            continue  # one retry, the model sometimes drifts from the format
    raise GeminiError("The coach gave an answer that couldn't be read")