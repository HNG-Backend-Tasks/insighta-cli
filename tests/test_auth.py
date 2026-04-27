from pathlib import Path
import json
import pytest
from unittest.mock import patch
from insighta.auth import save_credentials, load_credentials, clear_credentials, generate_pkce_pair, generate_state

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