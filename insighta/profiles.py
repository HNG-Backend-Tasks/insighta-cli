from typing import Optional

import typer
from rich.console import Console

from .display import print_pagination, print_profile_detail, print_profiles_table
from .http import APIClient

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


@app.command("get")
def get_profile(id: str = typer.Argument(...)):
    client = APIClient()
    with console.status("Fetching profile..."):
        response = client.get(f"/api/profiles/{id}")
    print_profile_detail(response.json()["data"])


@app.command("search")
def search_profiles(query: str = typer.Argument(...)):
    """Search profiles with natural language"""
    client = APIClient()
    with console.status("Searching..."):
        response = client.get("/api/profiles/search", params={"q": query})
    body = response.json()
    print_profiles_table(body["data"])
    print_pagination(body["page"], body["total_pages"], body["total"])


@app.command("create")
def create_profile(name: str = typer.Option(..., "--name")):
    client = APIClient()
    with console.status(f"Creating profile for {name}..."):
        response = client.post("/api/profiles", json={"name": name})

    if response.status_code == 403:
        typer.echo("Error: Only admins can create profiles.")
        raise typer.Exit(1)
    if response.status_code != 201:
        typer.echo(f"Error: {response.json().get('message', 'Something went wrong.')}")
        raise typer.Exit(1)

    print_profile_detail(response.json()["data"])

@app.command("delete")
def delete_profile(id: str = typer.Argument(...)):
    client = APIClient()
    with console.status(f"Deleting profile for {id}..."):
        response = client.post(f"/api/profiles/{id}")

    if response.status_code == 403:
        typer.echo("Error: Only admins can delete profiles.")
        raise typer.Exit(1)
    if response.status_code != 201:
        typer.echo(f"Error: {response.json().get('message', 'Something went wrong.')}")
        raise typer.Exit(1)

    print_profile_detail(response.json()["data"])

@app.command("export")
def export_profiles(
    format: str = typer.Option("csv", "--format"),
    gender: Optional[str] = typer.Option(None, "--gender"),
    country: Optional[str] = typer.Option(None, "--country"),
):
    from pathlib import Path

    params = {
        k: v
        for k, v in {
            "format": format,
            "gender": gender,
            "country_id": country,
        }.items()
        if v is not None
    }

    client = APIClient()
    with console.status("Exporting profiles..."):
        response = client.get("/api/profiles/export", params=params)

    disposition = response.headers.get("content-disposition", "")
    filename = (
        disposition.split("filename=")[-1]
        if "filename=" in disposition
        else f"profiles.{format}"
    )
    output_path = Path.cwd() / filename
    output_path.write_text(response.text)
    typer.echo(f"Saved to {output_path}")
