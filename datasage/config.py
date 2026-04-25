from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

CONFIG_DIR = Path.home() / ".datasage"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

LLMBackend = Literal["anthropic", "openai", "ollama"]


class Config(BaseModel):
    backend: LLMBackend = "anthropic"
    api_key: str = ""
    ollama_host: str = "http://localhost:11434"
    model: str = ""


def load_config() -> Config:
    if not CONFIG_FILE.exists():
        return Config()
    with open(CONFIG_FILE) as f:
        return Config(**yaml.safe_load(f))


def save_config(cfg: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(cfg.model_dump(), f)


def run_config_wizard() -> Config:
    """Interactive CLI config wizard (used by `datasage config`)."""
    from rich.console import Console
    from rich.prompt import Prompt

    console = Console()
    console.print("\n[bold green]datasage configuration wizard[/bold green]\n")

    backend = Prompt.ask(
        "LLM backend",
        choices=["anthropic", "openai", "ollama"],
        default="anthropic",
    )

    default_models = {
        "anthropic": "claude-opus-4-6",
        "openai": "gpt-4o",
        "ollama": "llama3",
    }

    api_key = ""
    ollama_host = "http://localhost:11434"

    if backend in ("anthropic", "openai"):
        api_key = Prompt.ask(f"{backend} API key", password=True)
    else:
        ollama_host = Prompt.ask("Ollama host", default="http://localhost:11434")

    model = Prompt.ask("Model name", default=default_models[backend])

    cfg = Config(backend=backend, api_key=api_key, ollama_host=ollama_host, model=model)
    save_config(cfg)
    console.print(f"\n[green]Config saved to {CONFIG_FILE}[/green]")
    return cfg
