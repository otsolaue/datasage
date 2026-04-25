import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="datasage — visual NLP pipeline builder")
console = Console()


@app.command()
def run(
    port: int = typer.Option(8501, help="Port to run the Streamlit app on"),
    browser: bool = typer.Option(True, help="Open browser automatically"),
):
    """Launch the datasage Streamlit UI."""
    app_path = Path(__file__).parent / "app.py"
    cmd = [
        sys.executable, "-m", "streamlit", "run", str(app_path),
        "--server.port", str(port),
        f"--server.headless={'false' if browser else 'true'}",
    ]
    console.print(f"[green]Starting datasage on http://localhost:{port}[/green]")
    subprocess.run(cmd)


@app.command()
def config():
    """Open the configuration wizard."""
    from datasage.config import run_config_wizard
    run_config_wizard()


if __name__ == "__main__":
    app()
