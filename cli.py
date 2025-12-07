# cli.py

from src.edge_tools.database import insert_minute_file_data
from src.edge_tools.utils.logger import setup_logging
import typer
import subprocess
import time
import webbrowser
import logging

logger = logging.getLogger(__name__)


app = typer.Typer(help="DJV Command Center 🔧")


@app.callback()
def main(
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug logging (sets logging.DEBUG)",
    ),
):
    level = logging.DEBUG if debug else logging.INFO
    setup_logging(level)
    logging.info(
        f"Logging level set to: {logging.getLevelName(logging.getLogger().getEffectiveLevel())}"
    )


# ───────────── SUBCOMMAND: API ─────────────
@app.command()
def dev(
    api_port: int = typer.Option(8000),
    front_port: int = typer.Option(5173),
):
    """Run the FastAPI backend."""
    typer.echo("⚙️ Starting FastAPI backend...")
    api_proc = subprocess.Popen(
        ["uvicorn", "api.main:app", "--reload", "--port", str(api_port)]
    )

    typer.echo("🎨 Starting Svelte frontend...")
    front_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd="front-svelte",  # adjust to your workspace
    )

    # Give frontend time to start
    time.sleep(2)

    url = f"http://localhost:{front_port}"
    typer.echo(f"🌐 Opening browser at {url}")
    webbrowser.open(url)

    typer.echo("🔥 Dev environment running. Press Ctrl+C to stop.")

    try:
        api_proc.wait()
        front_proc.wait()
    except KeyboardInterrupt:
        typer.echo("🛑 Shutting down…")
        api_proc.terminate()
        front_proc.terminate()


# ───────────── SUBCOMMAND: FRONTEND ─────────────
@app.command()
def frontend():
    typer.echo("🎨 Starting Svelte frontend...")
    front_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd="front-svelte",  # adjust to your workspace
    )
    return front_proc


@app.command()
def backend(api_port: int = typer.Option(8000)):
    """Run the FastAPI backend."""
    typer.echo("⚙️ Starting FastAPI backend...")
    api_proc = subprocess.Popen(
        [
            "uvicorn",
            "api.main:app",
            "--reload",
            "--port",
            str(api_port),
            "--host",
            "0.0.0.0",
        ]
    )
    return api_proc


# ───────────── SUBCOMMAND: INGEST ─────────────
@app.command()
def ingest(
    # date: str = typer.Option(None, help="Date to ingest (YYYY-MM-DD)"),
    # symbol: str = typer.Option("US500", help="Symbol to ingest"),
    # limit: int = typer.Option(0, help="Limit rows (0 = all)"),
):
    """Ingest OHLCV data into DuckDB."""
    insert_minute_file_data()
    # actual_ingest(symbol=symbol, date=date, limit=limit)


# ───────────── SUBCOMMAND: ANALYTICS ─────────────
@app.command()
def analytics(
    date: str = typer.Argument(..., help="Date (YYYY-MM-DD)"),
    regime: bool = typer.Option(False, help="Run opening-range regime classifier"),
):
    """Run analytics for a given date."""
    typer.echo(f"Running analytics for {date}, regime={regime}")
    # run your analytics module


# ───────────── SUBCOMMAND: STREAMLIT ─────────────
@app.command()
def dashboard(
    port: int = typer.Option(8501, help="Port for streamlit"),
):
    typer.echo(f"Starting Streamlit on port {port}")
    # subprocess.run(["streamlit", "run", "dashboard.py", "--server.port", str(port)])


if __name__ == "__main__":
    app()
