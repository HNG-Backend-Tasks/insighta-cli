import json
import hashlib
import base64
import secrets
import socket
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


CREDENTIALS_PATH = Path.home() / ".insighta" / "credentials.json"


def save_credentials(access_token: str, refresh_token: str, username: str) -> None:
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.write_text(
        json.dumps(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "username": username,
            }
        )
    )


def load_credentials() -> dict | None:
    if not CREDENTIALS_PATH.exists():
        return None
    return json.loads(CREDENTIALS_PATH.read_text())


def clear_credentials() -> None:
    if CREDENTIALS_PATH.exists():
        CREDENTIALS_PATH.unlink()


def generate_pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def generate_state() -> str:
    return secrets.token_urlsafe(16)


class _CallbackHandler(BaseHTTPRequestHandler):
    code: str | None = None
    state: str | None = None

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        _CallbackHandler.code = params.get("code", [None])[0]
        _CallbackHandler.state = params.get("state", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Login successful. You can close this tab.")

    def log_message(self, format, *args):
        pass


def start_callback_server() -> tuple[HTTPServer, int]:
    with socket.socket() as s:
        s.bind(("localhost", 0))
        port = s.getsockname()[1]

    server = HTTPServer(("localhost", port), _CallbackHandler)

    def handle_one_request():
        server.handle_request()  # blocks until one request arrives
        return _CallbackHandler.code, _CallbackHandler.state

    server.handle_one_request = handle_one_request
    return server, port
