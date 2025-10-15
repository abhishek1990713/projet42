"""
Test Cases for main.py (Feedback API)

These tests verify:
1. Feedback submission API (/feedback_service)
2. Aggregated report API (/aggregated_report)
3. Database rollback and error handling
"""

from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

# ---------------------------
# SAMPLE TEST DATA
# ---------------------------
headers = {
    "x-correlation-id": "test-corr-123",
    "x-application-id": "test-app-001",
    "x-created-by": "test_user",
    "x-document-id": "doc-123",
    "x-file-id": "file-999",
    "x-authorization-coin": "auth-001",
    "x-feedback-source": "test_source"
}

payload = {
    "Document_type": "passport",
    "field_feedback": {
        "Name": {"status": "thumbs_up"},
        "Address": {"status": "thumbs_down"},
        "DOB": {"status": "thumbs_up"}
    }
}

# ---------------------------
# TEST CASES
# ---------------------------

def test_feedback_service_success():
    """
    ✅ Test successful feedback submission.
    Expect: 201 Created with success message.
    """
    response = client.post("/feedback_service", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["SUCCESS"] is True
    assert "feedback_id" in data["details"]
    assert data["message"] == "Data inserted successfully"


def test_feedback_service_missing_header():
    """
    ⚠️ Test missing required headers.
    Expect: 400 Bad Request.
    """
    incomplete_headers = headers.copy()
    incomplete_headers.pop("x-application-id")

    response = client.post("/feedback_service", json=payload, headers=incomplete_headers)
    assert response.status_code == 400


def test_aggregated_report_success(monkeypatch):
    """
    ✅ Test combined report fetching with mock data.
    Expect: 200 OK with structured report output.
    """

    def mock_get_doc_stats(app_id, start, end):
        return [{"application_id": app_id, "Document_Percentage": 85.4}]

    def mock_feedback_report(app_id, start, end):
        return [{"application_id": app_id, "Field_Name": {"Name": {"Field_Level_Accuracy": 90.0}}}]

    monkeypatch.setattr("document_stats.get_document_percentage_stats", mock_get_doc_stats)
    monkeypatch.setattr("feedback_report.feedback_report", mock_feedback_report)

    params = {"start_date": "2025-10-10", "end_date": "2025-10-15"}
    response = client.get("/aggregated_report", headers={"application_id": "test-app-001"}, params=params)

    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert result[0]["report_type"] == "high_level"
    assert "Field_Name" in result[1]


def test_aggregated_report_missing_params():
    """
    ⚠️ Test missing query parameters.
    Expect: 400 Bad Request.
    """
    response = client.get("/aggregated_report", headers={"application_id": "test-app-001"})
    assert response.status_code == 400


def test_feedback_service_invalid_json():
    """
    ⚠️ Test invalid JSON format.
    Expect: 400 Bad Request.
    """
    response = client.post("/feedback_service", data="invalid-json", headers=headers)
    assert response.status_code == 400
