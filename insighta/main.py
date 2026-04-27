import typer
from . import auth, profiles

app = typer.Typer(help="Insighta Labs+ CLI")

app.add_typer(auth.app, name="auth")
app.add_typer(profiles.app, name="profiles")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())

if __name__ == "__main__":
    app()