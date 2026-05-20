from fastapi.testclient import TestClient
from main import app
from helpers import assert_route_error

client = TestClient(app)


def test_next_payday_summary_route(test_db):
    response = client.get("/summaries/next-payday?today=2026-05-14")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["today"] == "2026-05-14"
    assert body["next_payday"] == "2026-05-15"
    assert body["payments"] == []


def test_next_payday_summary_route_invalid_date(test_db):
    response = client.get("/summaries/next-payday?today=05/14/2026")

    assert_route_error(response, 400, "INVALID_DATE_FORMAT")
