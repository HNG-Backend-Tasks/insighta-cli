import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from insighta.main import app

runner = CliRunner()

MOCK_CREDS = {
    "access_token": "access123",
    "refresh_token": "refresh456",
    "username": "danielpopoola",
}

MOCK_LIST_RESPONSE = {
    "status": "success",
    "page": 1,
    "limit": 10,
    "total": 2,
    "total_pages": 1,
    "links": {"self": "/api/profiles?page=1&limit=10", "next": None, "prev": None},
    "data": [
        {
            "id": "abc-123",
            "name": "Kwame",
            "gender": "male",
            "age": 25,
            "age_group": "adult",
            "country_id": "NG",
        },
        {
            "id": "def-456",
            "name": "Amina",
            "gender": "female",
            "age": 17,
            "age_group": "teenager",
            "country_id": "KE",
        },
    ],
}


def test_profiles_list_displays_table():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_LIST_RESPONSE

    with (
        patch("insighta.http.load_credentials", return_value=MOCK_CREDS),
        patch("httpx.Client.request", return_value=mock_response),
    ):
        result = runner.invoke(app, ["profiles", "list"])

    assert result.exit_code == 0
    assert "Kwame" in result.output
    assert "Amina" in result.output


def test_profiles_get_displays_detail():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "success",
        "data": {
            "id": "abc-123",
            "name": "Kwame",
            "gender": "male",
            "age": 25,
            "age_group": "adult",
            "country_id": "NG",
            "country_name": "Nigeria",
            "gender_probability": 0.95,
            "country_probability": 0.85,
            "created_at": "2026-01-01",
        },
    }

    with (
        patch("insighta.http.load_credentials", return_value=MOCK_CREDS),
        patch("httpx.Client.request", return_value=mock_response),
    ):
        result = runner.invoke(app, ["profiles", "get", "abc-123"])

    assert result.exit_code == 0
    assert "Kwame" in result.output


def test_profiles_search_displays_results():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_LIST_RESPONSE

    with (
        patch("insighta.http.load_credentials", return_value=MOCK_CREDS),
        patch("httpx.Client.request", return_value=mock_response),
    ):
        result = runner.invoke(app, ["profiles", "search", "young males from nigeria"])

    assert result.exit_code == 0
    assert "Kwame" in result.output


def test_profiles_create_displays_new_profile():
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "status": "success",
        "data": {
            "id": "new-123",
            "name": "Harriet",
            "gender": "female",
            "age": 28,
            "age_group": "adult",
            "country_id": "US",
            "country_name": "United States",
            "gender_probability": 0.97,
            "country_probability": 0.89,
            "created_at": "2026-01-01",
        },
    }

    with (
        patch("insighta.http.load_credentials", return_value=MOCK_CREDS),
        patch("httpx.Client.request", return_value=mock_response),
    ):
        result = runner.invoke(app, ["profiles", "create", "--name", "Harriet"])

    assert result.exit_code == 0
    assert "Harriet" in result.output


def test_profiles_export_saves_csv(tmp_path):
    csv_content = "id,name,gender\nabc-123,Kwame,male\n"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = csv_content
    mock_response.headers = {
        "content-disposition": "attachment; filename=profiles_20260427.csv"
    }

    with (
        patch("insighta.http.load_credentials", return_value=MOCK_CREDS),
        patch("httpx.Client.request", return_value=mock_response),
        patch("pathlib.Path.cwd", return_value=tmp_path),
    ):
        result = runner.invoke(app, ["profiles", "export", "--format", "csv"])

    assert result.exit_code == 0
    assert "saved" in result.output.lower()
