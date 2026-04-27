from rich.console import Console
from rich.table import Table

console = Console()


def print_profiles_table(profiles: list[dict]) -> None:
    if not profiles:
        console.print("[yellow]No profiles found.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=36)
    table.add_column("Name")
    table.add_column("Gender")
    table.add_column("Age")
    table.add_column("Age Group")
    table.add_column("Country")

    for p in profiles:
        table.add_row(
            p["id"],
            p["name"],
            p["gender"],
            str(p["age"]),
            p["age_group"],
            p["country_id"],
        )

    console.print(table)


def print_profile_detail(profile: dict) -> None:
    table = Table(show_header=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    for key, value in profile.items():
        table.add_row(key, str(value))

    console.print(table)


def print_pagination(page: int, total_pages: int, total: int) -> None:
    console.print(f"\n[dim]Page {page} of {total_pages} ({total} total)[/dim]")
