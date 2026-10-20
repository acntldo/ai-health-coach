from datetime import date

ME = {"X-Device-ID": "test-device-1"}
OTHER = {"X-Device-ID": "other-device-1"}


def test_health_needs_no_device_id(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_missing_or_malformed_device_id_is_rejected(client):
    assert client.get("/api/days").status_code == 422
    assert client.get("/api/days", headers={"X-Device-ID": "short"}).status_code == 422
    assert client.get("/api/days", headers={"X-Device-ID": "bad id!!!!"}).status_code == 422


def test_device_id_cannot_match_the_global_usage_row(client):
    # the overall usage cap is stored under "__global__", underscores aren't allowed
    assert client.get("/api/days", headers={"X-Device-ID": "__global__"}).status_code == 422


def test_days_are_listed_newest_first_with_totals(client, add_entry):
    add_entry(day=date(2026, 10, 18), name="banana", calories=105)
    add_entry(day=date(2026, 10, 18), name="apple", calories=95)
    add_entry(day=date(2026, 10, 19), name="rice", calories=205)

    res = client.get("/api/days", headers=ME)
    assert res.json() == [
        {"day": "2026-10-19", "total": 205},
        {"day": "2026-10-18", "total": 200},
    ]


def test_day_detail_lists_entries_and_total(client, add_entry):
    add_entry(name="banana", calories=105)
    add_entry(name="apple", calories=95)

    body = client.get("/api/days/2026-10-18", headers=ME).json()
    assert body["total"] == 200
    assert [e["name"] for e in body["entries"]] == ["banana", "apple"]


def test_empty_day_returns_zero_not_404(client):
    res = client.get("/api/days/2026-10-18", headers=ME)
    assert res.status_code == 200
    assert res.json()["total"] == 0
    assert res.json()["entries"] == []


def test_devices_only_see_their_own_data(client, add_entry):
    add_entry(device_id="test-device-1")

    assert client.get("/api/days", headers=OTHER).json() == []
    assert client.get("/api/days/2026-10-18", headers=OTHER).json()["total"] == 0


def test_delete_removes_entry_and_updates_total(client, add_entry):
    add_entry(name="rice", calories=205)
    gone = add_entry(name="banana", calories=105)

    assert client.delete(f"/api/entries/{gone}", headers=ME).status_code == 204
    assert client.get("/api/days/2026-10-18", headers=ME).json()["total"] == 205


def test_cannot_delete_another_devices_entry(client, add_entry):
    entry_id = add_entry(device_id="test-device-1")

    assert client.delete(f"/api/entries/{entry_id}", headers=OTHER).status_code == 404
    # the entry is still there for its owner
    assert client.get("/api/days/2026-10-18", headers=ME).json()["total"] == 105


def test_delete_missing_entry_returns_404(client):
    assert client.delete("/api/entries/999", headers=ME).status_code == 404


def test_messages_are_oldest_first_and_capped_at_50(client, add_message):
    for i in range(55):
        add_message(text=f"msg {i}")

    messages = client.get("/api/messages", headers=ME).json()
    assert len(messages) == 50
    assert messages[0]["text"] == "msg 5"
    assert messages[-1]["text"] == "msg 54"