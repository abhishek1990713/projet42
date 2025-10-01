# test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# -----------------------
# INVALID DATE FORMAT
# -----------------------
def test_fetch_feedback_invalid_date_format():
    """Should return 400 when date format is invalid"""
    response = client.get(
        "/fetch_feedback",
        params={
            "application_id": "sa1236",
            "document_id": "123",
            "start_day": "2025-13-01",  # invalid month
            "end_day": "2025-10-01"
        },
    )
    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]


# -----------------------
# MISSING RECORDS
# -----------------------
def test_fetch_feedback_no_records(monkeypatch):
    """Should return 404 when no feedback records exist"""

    # Mock DB query
    def mock_query(*args, **kwargs):
        class MockQuery:
            def filter(self, *a, **k): return self
            def order_by(self, *a, **k): return self
            def all(self): return []
        return MockQuery()

    # Patch get_db and Session.query
    monkeypatch.setattr("main.get_db", lambda: None)
    monkeypatch.setattr("main.Session", type("Session", (), {"query": mock_query}))

    response = client.get(
        "/fetch_feedback",
        params={
            "application_id": "sa1236",
            "document_id": "123",
            "start_day": "2025-09-01",
            "end_day": "2025-09-30"
        },
    )

    assert response.status_code == 404
    assert "No records found" in response.json()["detail"]


# -----------------------
# SUCCESSFUL FETCH
# -----------------------
def test_fetch_feedback_success(monkeypatch):
    """Should return 200 with feedback records"""

    class MockFeedback:
        id = 1
        application_id = "sa1236"
        document_id = "123"
        created_at = "2025-09-10 12:00:00"
        feedback = {"msg": "test feedback"}

    def mock_query(*args, **kwargs):
        class MockQuery:
            def filter(self, *a, **k): return self
            def order_by(self, *a, **k): return self
            def all(self): return [MockFeedback()]
        return MockQuery()

    monkeypatch.setattr("main.get_db", lambda: None)
    monkeypatch.setattr("main.Session", type("Session", (), {"query": mock_query}))

    response = client.get(
        "/fetch_feedback",
        params={
            "application_id": "sa1236",
            "document_id": "123",
            "start_day": "2025-09-01",
            "end_day": "2025-09-30"
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["application_id"] == "sa1236"
    assert data[0]["document_id"] == "123"
    assert data[0]["feedback"]["msg"] == "test feedback"


# -----------------------
# INTERNAL SERVER ERROR
# -----------------------
def test_fetch_feedback_internal_error(monkeypatch):
    """Should return 500 if DB query raises exception"""

    def mock_query_fail(*args, **kwargs):
        raise Exception("DB failure")

    monkeypatch.setattr("main.get_db", lambda: None)
    monkeypatch.setattr("main.Session", type("Session", (), {"query": mock_query_fail}))

    response = client.get(
        "/fetch_feedback",
        params={
            "application_id": "sa1236",
            "document_id": "123",
            "start_day": "2025-09-01",
            "end_day": "2025-09-30"
        },
    )

    assert response.status_code == 500
    assert "DB failure" in response.json()["detail"]


# -----------------------
# MISSING PARAMETERS
# -----------------------
def test_fetch_feedback_missing_application_id():
    """Should return 422 when application_id is missing"""
    response = client.get(
        "/fetch_feedback",
        params={
            "document_id": "123",
            "start_day": "2025-09-01",
            "end_day": "2025-09-30",
        },
    )
    assert response.status_code == 422


def test_fetch_feedback_missing_document_id():
    """Should return 422 when document_id is missing"""
    response = client.get(
        "/fetch_feedback",
        params={
            "application_id": "sa1236",
            "start_day": "2025-09-01",
            "end_day": "2025-09-30",
        },
    )
    assert response.status_code == 422
