import typer
from typing import Optional
from rich.console import Console
from .http import APIClient
from .display import print_profiles_table, print_pagination

app = typer.Typer(help="Manage profiles")
console = Console()


@app.command("list")
def list_profiles(
    gender: Optional[str] = typer.Option(None, "--gender"),
    country: Optional[str] = typer.Option(None, "--country"),
    age_group: Optional[str] = typer.Option(None, "--age-group"),
    min_age: Optional[int] = typer.Option(None, "--min-age"),
    max_age: Optional[int] = typer.Option(None, "--max-age"),
    sort_by: Optional[str] = typer.Option(None, "--sort-by"),
    order: Optional[str] = typer.Option(None, "--order"),
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(10, "--limit"),
):
    """List profiles with optional filters"""
    params = {
        k: v
        for k, v in {
            "gender": gender,
            "country_id": country,
            "age_group": age_group,
            "min_age": min_age,
            "max_age": max_age,
            "sort_by": sort_by,
            "order": order,
            "page": page,
            "limit": limit,
        }.items()
        if v is not None
    }

    client = APIClient()
    with console.status("Fetching profiles..."):
        response = client.get("/api/profiles", params=params)

    body = response.json()
    print_profiles_table(body["data"])
    print_pagination(body["page"], body["total_pages"], body["total"])
