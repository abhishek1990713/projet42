# test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import Session

client = TestClient(app)

# -----------------------
# Dummy DB session
# -----------------------
class DummyQuery:
    def filter(self, *args, **kwargs):
        return self
    def order_by(self, *args, **kwargs):
        return self
    def all(self):
        return []

class DummySession:
    def query(self, *args, **kwargs):
        return DummyQuery()

def get_dummy_db():
    # FastAPI expects a generator
    yield DummySession()


# Override the DB dependency
app.dependency_overrides[get_db] = get_dummy_db


# -----------------------
# TEST CASES
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


def test_fetch_feedback_no_records():
    """Should return 404 when no feedback records exist"""
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


def test_fetch_feedback_success():
    """Should return 200 with feedback records"""

    class MockFeedback:
        id = 1
        application_id = "sa1236"
        document_id = "123"
        created_at = "2025-09-10 12:00:00"
        feedback = {"msg": "test feedback"}

    # Override DummyQuery to return a record
    class SuccessQuery(DummyQuery):
        def all(self):
            return [MockFeedback()]

    class SuccessSession(DummySession):
        def query(self, *args, **kwargs):
            return SuccessQuery()

    def get_success_db():
        yield SuccessSession()

    app.dependency_overrides[get_db] = get_success_db

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


def test_fetch_feedback_missing_application_id():
    """Should return 422 when application_id is missing"""
    response = client.get(
        "/fetch_feedback",
        params={
            "document_id": "123",
            "start_day": "2025-09-01",
            "end_day": "2025-09-30"
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
            "end_day": "2025-09-30"
        },
    )
    assert response.status_code == 422
