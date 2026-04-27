import httpx
import typer

from .auth import load_credentials, save_credentials, clear_credentials
from .config import settings


class APIClient:
    def __init__(self):
        creds = load_credentials()
        if not creds:
            typer.echo("Not logged in. Run: insighta login")
            raise typer.Exit(1)
        self._creds = creds
        self._client = httpx.Client(base_url=settings.API_BASE_URL)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._creds['access_token']}",
            "X-API-Version": "1",
        }

    def _refresh(self) -> bool:
        response = self._client.post(
            "/auth/refresh",
            json={"refresh_token": self._creds["refresh_token"]},
        )
        if response.status_code == 200:
            data = response.json()
            save_credentials(
                data["access_token"], data["refresh_token"], self._creds["username"]
            )
            self._creds = load_credentials()
            return True
        clear_credentials()
        return False

    def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        response = self._client.request(method, path, headers=self._headers(), **kwargs)
        if response.status_code == 401:
            if self._refresh():
                return self._client.request(
                    method, path, headers=self._headers(), **kwargs
                )
            typer.echo("Session expired. Run: insighta login")
            raise typer.Exit(1)
        return response

    def get(self, path: str, **kwargs) -> httpx.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> httpx.Response:
        return self.request("POST", path, **kwargs)

    def delete(self, path: str, **kwargs) -> httpx.Response:
        return self.request("DELETE", path, **kwargs)
