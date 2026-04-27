import json
from pathlib import Path

CREDENTIALS_PATH = Path.home() / ".insighta" / "credentials.json"

def save_credentials(access_token: str, refresh_token: str, username: str) -> None:
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.write_text(json.dumps({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "username": username,
    }))

def load_credentials() -> dict | None:
    if not CREDENTIALS_PATH.exists():
        return None
    return json.loads(CREDENTIALS_PATH.read_text())

def clear_credentials() -> None:
    if CREDENTIALS_PATH.exists():
        CREDENTIALS_PATH.unlink()