import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from insighta.main import app

runner = CliRunner()

MOCK_CREDS = {
    "access_token": "access123",
    "refresh_token": "refresh456",
    "username": "danielpopoola"
}

MOCK_LIST_RESPONSE = {
    "status": "success",
    "page": 1,
    "limit": 10,
    "total": 2,
    "total_pages": 1,
    "links": {"self": "/api/profiles?page=1&limit=10", "next": None, "prev": None},
    "data": [
        {"id": "abc-123", "name": "Kwame", "gender": "male", "age": 25, "age_group": "adult", "country_id": "NG"},
        {"id": "def-456", "name": "Amina", "gender": "female", "age": 17, "age_group": "teenager", "country_id": "KE"},
    ]
}

def test_profiles_list_displays_table():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_LIST_RESPONSE

    with patch("insighta.http.load_credentials", return_value=MOCK_CREDS), \
         patch("httpx.Client.request", return_value=mock_response):
        result = runner.invoke(app, ["profiles", "list"])

    assert result.exit_code == 0
    assert "Kwame" in result.output
    assert "Amina" in result.output

