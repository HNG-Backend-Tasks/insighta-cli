import pytest
import threading
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from insighta.main import app
from insighta.auth import (
    save_credentials,
    load_credentials,
    clear_credentials,
    generate_pkce_pair,
    generate_state,
    start_callback_server,
)

runner = CliRunner()

@pytest.fixture(autouse=True)
def temp_credentials(tmp_path):
    fake_path = tmp_path / ".insighta" / "credentials.json"
    with patch("insighta.auth.CREDENTIALS_PATH", fake_path):
        yield fake_path

def test_credentials_can_be_saved_and_loaded(temp_credentials):
    save_credentials("access123", "refresh456", "danielpopoola")
    loaded = load_credentials()
    assert loaded["access_token"] == "access123"
    assert loaded["refresh_token"] == "refresh456"
    assert loaded["username"] == "danielpopoola"

def test_load_credentials_returns_none_when_missing(temp_credentials):
    result = load_credentials()
    assert result is None

def test_clear_credentials_removes_file(temp_credentials):
    save_credentials("access123", "refresh456", "danielpopoola")
    clear_credentials()
    assert load_credentials() is None

def test_pkce_pair_generates_valid_challenge():
    verifier, challenge = generate_pkce_pair()
    
    import hashlib, base64
    expected = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    
    assert challenge == expected
    assert len(verifier) > 30

def test_state_is_random():
    state1 = generate_state()
    state2 = generate_state()
    assert state1 != state2
    assert len(state1) > 10

def test_callback_server_captures_code_and_state():
    server, port = start_callback_server()
    
    def send_callback():
        import httpx
        httpx.get(f"http://localhost:{port}/callback?code=testcode&state=teststate")
    
    thread = threading.Thread(target=send_callback)
    thread.start()
    
    code, state = server.handle_one_request()
    thread.join()
    
    assert code == "testcode"
    assert state == "teststate"

def test_login_command_saves_credentials(tmp_path):
    fake_path = tmp_path / ".insighta" / "credentials.json"
    
    mock_server = MagicMock()
    mock_server.handle_one_request.return_value = ("testcode", "teststate")   

    mock_whoami_response = MagicMock()
    mock_whoami_response.status_code = 200
    mock_whoami_response.json.return_value = {"login": "danielpopoola"}

    with patch("insighta.auth.CREDENTIALS_PATH", fake_path), \
         patch("insighta.auth.generate_pkce_pair", return_value=("verifier", "challenge")), \
         patch("insighta.auth.generate_state", return_value="teststate"), \
         patch("insighta.auth.start_callback_server", return_value=(mock_server, 8765)), \
         patch("insighta.auth.webbrowser.open"), \
         patch("insighta.auth.exchange_code_with_backend", return_value={"access_token": "access123", "refresh_token": "refresh456"}), \
         patch("insighta.auth.fetch_github_username", return_value="danielpopoola"):

        result = runner.invoke(app, ["login"])

    assert result.exit_code == 0
    assert "danielpopoola" in result.output
