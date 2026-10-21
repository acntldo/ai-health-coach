from datetime import datetime, timezone

import pytest

from app.coach import CoachResult, LoggedItem
from app.gemini import GeminiError
from app.usage import LimitReached
from app.usda import UsdaError

ME = {"X-Device-ID": "test-device-1"}
OTHER = {"X-Device-ID": "other-device-1"}


def today():
    return datetime.now(timezone.utc).date().isoformat()


def rice_result():
    item = LoggedItem(
        name="white rice",
        serving="1 cup cooked",
        grams=158,
        calories=205,
        confidence="high",
        usda_food_id=2710788,
        usda_description="Rice, white, cooked",
    )
    return CoachResult(reply="Logged rice", items=[item])


def fake_coach(monkeypatch, result=None, error=None):
    """Replaces the real coach and records what it was called with."""
    calls = []

    def fake(message, history, day_entries):
        calls.append({"message": message, "history": history, "day_entries": day_entries})
        if error:
            raise error
        return result

    monkeypatch.setattr("app.routers.chat.run_coach", fake)
    return calls


def post(client, message="I had rice", headers=ME, day=None):
    return client.post("/api/chat", json={"message": message, "day": day or today()}, headers=headers)


def test_chat_logs_food_and_returns_total(client, monkeypatch):
    fake_coach(monkeypatch, rice_result())
    body = post(client).json()

    assert body["reply"] == "Logged rice"
    assert body["day_total"] == 205
    assert [e["name"] for e in body["entries"]] == ["white rice"]
    assert body["entries"][0]["confidence"] == "high"
    # the same food shows up in the day view
    assert client.get(f"/api/days/{today()}", headers=ME).json()["total"] == 205


def test_both_messages_are_saved(client, monkeypatch):
    fake_coach(monkeypatch, rice_result())
    post(client)

    saved = client.get("/api/messages", headers=ME).json()
    assert [(m["role"], m["text"]) for m in saved] == [("user", "I had rice"), ("coach", "Logged rice")]


def test_message_without_food_logs_nothing(client, monkeypatch):
    fake_coach(monkeypatch, CoachResult(reply="Paris!"))
    body = post(client, "what is the capital of France?").json()

    assert body["entries"] == []
    assert body["day_total"] == 0
    assert len(client.get("/api/messages", headers=ME).json()) == 2


def test_coach_receives_history_and_todays_log(client, monkeypatch):
    calls = fake_coach(monkeypatch, rice_result())
    post(client, "I had rice")
    post(client, "how am I doing?")

    assert calls[1]["history"] == [("user", "I had rice"), ("coach", "Logged rice")]
    assert calls[1]["day_entries"] == [("white rice", 205)]


def test_other_device_gets_no_history(client, monkeypatch):
    calls = fake_coach(monkeypatch, rice_result())
    post(client, "I had rice", headers=ME)
    post(client, "hello", headers=OTHER)

    assert calls[1]["history"] == []
    assert calls[1]["day_entries"] == []


@pytest.mark.parametrize("error", [GeminiError("secret detail"), UsdaError("secret detail")])
def test_coach_failure_returns_503_and_saves_nothing(client, monkeypatch, error):
    fake_coach(monkeypatch, error=error)
    res = post(client)

    assert res.status_code == 503
    assert "secret" not in res.json()["detail"]  # real cause stays in the log
    assert client.get("/api/messages", headers=ME).json() == []
    assert client.get("/api/days", headers=ME).json() == []


@pytest.mark.parametrize("scope", ["device", "global"])
def test_limit_reached_returns_429_without_calling_the_coach(client, monkeypatch, scope):
    calls = fake_coach(monkeypatch, rice_result())

    def blocked(*args, **kwargs):
        raise LimitReached(scope)

    monkeypatch.setattr("app.routers.chat.consume", blocked)
    res = post(client)

    assert res.status_code == 429
    assert "midnight UTC" in res.json()["detail"]
    assert calls == []


def test_date_far_from_today_is_rejected(client, monkeypatch):
    calls = fake_coach(monkeypatch, rice_result())

    assert post(client, day="2020-01-01").status_code == 422
    assert calls == []


@pytest.mark.parametrize("message", ["", "   ", "a" * 501])
def test_bad_messages_are_rejected(client, monkeypatch, message):
    fake_coach(monkeypatch, rice_result())
    assert post(client, message).status_code == 422


def test_missing_device_id_is_rejected(client):
    res = client.post("/api/chat", json={"message": "hi", "day": today()})
    assert res.status_code == 422