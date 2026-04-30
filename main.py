import sys
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

console = Console()


@click.group()
def cli():
    """School automation bot powered by Claude."""
    pass


@cli.command()
def setup():
    """Validate configuration and test API connections."""
    from bot.config import Config

    console.print(Panel("[bold]School Bot Setup Check[/bold]", expand=False))

    errors = Config.validate()
    if errors:
        console.print("[red]Configuration errors:[/red]")
        for err in errors:
            console.print(f"  [red]✗[/red] {err}")
        console.print("\nCopy [cyan].env.example[/cyan] to [cyan].env[/cyan] and fill in your values.")
        sys.exit(1)

    console.print("[green]✓[/green] Configuration looks good")

    console.print("\nTesting Canvas connection...")
    try:
        from bot.canvas_client import CanvasClient
        client = CanvasClient()
        result = client.list_courses()
        import json
        courses = json.loads(result)
        if isinstance(courses, list):
            console.print(f"[green]✓[/green] Canvas connected — {len(courses)} active course(s) found")
        else:
            console.print(f"[yellow]⚠[/yellow] Canvas responded but returned: {result}")
    except Exception as e:
        console.print(f"[red]✗[/red] Canvas connection failed: {e}")

    console.print("\nTesting Google connection...")
    try:
        from bot.google_client import GoogleClient
        gclient = GoogleClient()
        result = gclient.list_docs(max_results=1)
        console.print("[green]✓[/green] Google APIs connected")
    except Exception as e:
        console.print(f"[red]✗[/red] Google connection failed: {e}")
        console.print("  Run [cyan]python setup_google_auth.py[/cyan] to authenticate with Google.")

    console.print("\n[bold green]Setup complete! Run [cyan]python main.py chat[/cyan] to start.[/bold green]")


@cli.command()
def chat():
    """Start an interactive chat session with the school bot."""
    from bot.config import Config
    from bot.agent import SchoolAgent

    errors = Config.validate()
    if errors:
        console.print("[red]Configuration errors (run 'python main.py setup' for details):[/red]")
        for err in errors:
            console.print(f"  [red]✗[/red] {err}")
        sys.exit(1)

    console.print(Panel(
        "[bold cyan]School Bot[/bold cyan]\n"
        "Ask me to check assignments, submit work, draft emails, create Google Docs, and more.\n"
        "Type [bold]exit[/bold] or [bold]quit[/bold] to stop.",
        expand=False
    ))

    agent = SchoolAgent()

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            console.print("[dim]Goodbye![/dim]")
            break

        with console.status("[dim]Thinking...[/dim]", spinner="dots"):
            response = agent.chat(user_input)

        console.print()
        console.print(Text("Bot:", style="bold green"), end=" ")
        try:
            console.print(Markdown(response))
        except Exception:
            console.print(response)


if __name__ == "__main__":
    cli()
