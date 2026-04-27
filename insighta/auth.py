import base64
import hashlib
import json
import secrets
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
import typer

from .config import settings

app = typer.Typer()

CALLBACK_PORT = 8765
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
    server = HTTPServer(("localhost", CALLBACK_PORT), _CallbackHandler)

    def handle_one_request():
        server.handle_request()  # blocks until one request arrives
        return _CallbackHandler.code, _CallbackHandler.state

    server.handle_one_request = handle_one_request
    return server, CALLBACK_PORT


@app.command()
def login():
    verifier, challenge = generate_pkce_pair()
    state = generate_state()
    server, _ = start_callback_server()

    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": f"http://localhost:{CALLBACK_PORT}/callback",
        "scope": "user:email",
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{settings.GITHUB_AUTHORIZE_URL}?{query}"

    typer.echo("Opening GitHub login in your browser...")
    webbrowser.open(url)

    code, returned_state = server.handle_one_request()

    if returned_state != state:
        typer.echo("State mismatch — possible CSRF attack. Aborting.")
        raise typer.Exit(1)

    data = exchange_code_with_backend(code, state, verifier)
    username = data['username']
    save_credentials(data["access_token"], data["refresh_token"], username)
    typer.echo(f"Logged in as @{username}")


@app.command()
def logout():
    creds = load_credentials()
    if not creds:
        typer.echo("Not logged in.")
        raise typer.Exit(1)

    with httpx.Client(timeout=10.0) as client:
        client.post(
            f"{settings.API_BASE_URL}/auth/logout",
            json={"refresh_token": creds["refresh_token"]},
        )

    clear_credentials()
    typer.echo("Logged out.")


@app.command()
def whoami():
    creds = load_credentials()
    if not creds:
        typer.echo("Not logged in.")
        raise typer.Exit(1)
    typer.echo(f"Logged in as @{creds['username']}")


def exchange_code_with_backend(code: str, state: str, verifier: str) -> dict:
    with httpx.Client(timeout=15.0) as client:
        response = client.get(
            f"{settings.API_BASE_URL}/auth/github/callback",
            params={
                "code": code,
                "state": state,
                "code_verifier": verifier,
                "client_source": "cli",
            },
        )
    if response.status_code != 200:
        typer.echo("Login failed. Please try again.")
        raise typer.Exit(1)
    return response.json()

