import pytest
from unittest.mock import patch, MagicMock
from insighta.http import APIClient

@pytest.fixture
def mock_credentials():
    creds = {
        "access_token": "valid_access_token",
        "refresh_token": "valid_refresh_token",
        "username": "danielpopoola"
    }
    with patch("insighta.http.load_credentials", return_value=creds):
        yield creds

def test_client_attaches_auth_headers(mock_credentials):
    with patch("httpx.Client.request") as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        client = APIClient()
        client.get("/api/profiles")

        call_headers = mock_request.call_args.kwargs["headers"]
        assert call_headers["Authorization"] == "Bearer valid_access_token"
        assert call_headers["X-API-Version"] == "1"