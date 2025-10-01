# test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ---------- TEST CASES ----------

def test_fetch_feedback_invalid_date_format():
    """Should return 400 when date format is invalid"""
    response = client.get(
        "/fetch_feedback",
        params={
            "application_id": "123",
            "document_id": "456",
            "start_day": "2025-13-01",  # invalid month
            "end_day": "2025-10-01"
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid date format. Use YYYY-MM-DD"


def test_fetch_feedback_no_records(monkeypatch):
    """Should return 404 when no feedback records exist"""

    # Mock DB query result
    def mock_query(*args, **kwargs):
        class MockQuery:
            def filter(self, *a, **k): return self
            def order_by(self, *a, **k): return self
            def all(self): return []
        return MockQuery()

    # Patch the DB session dependency
    monkeypatch.setattr("main.get_db", lambda: None)
    monkeypatch.setattr("main.Session.query", mock_query)

    response = client.get(
        "/fetch_feedback",
        params={
            "application_id": "123",
            "document_id": "456",
            "start_day": "2025-09-01",
            "end_day": "2025-09-30",
        },
    )

    assert response.status_code == 404
    assert "No records found" in response.json()["detail"]


def test_fetch_feedback_success(monkeypatch):
    """Should return 200 with feedback records"""

    class MockFeedback:
        id = 1
        application_id = "123"
        document_id = "456"
        created_at = "2025-09-10 12:00:00"
        feedback = {"msg": "test feedback"}  # assuming you renamed column

    def mock_query(*args, **kwargs):
        class MockQuery:
            def filter(self, *a, **k): return self
            def order_by(self, *a, **k): return self
            def all(self): return [MockFeedback()]
        return MockQuery()

    monkeypatch.setattr("main.get_db", lambda: None)
    monkeypatch.setattr("main.Session.query", mock_query)

    response = client.get(
        "/fetch_feedback",
        params={
            "application_id": "123",
            "document_id": "456",
            "start_day": "2025-09-01",
            "end_day": "2025-09-30",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["application_id"] == "123"
    assert data[0]["document_id"] == "456"
