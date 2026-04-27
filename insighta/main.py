import typer

from . import auth, profiles

app = typer.Typer(help="Insighta Labs+ CLI")

app.command("login")(auth.login)
app.command("logout")(auth.logout)
app.command("whoami")(auth.whoami)

app.add_typer(profiles.app, name="profiles")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


if __name__ == "__main__":
    app()
