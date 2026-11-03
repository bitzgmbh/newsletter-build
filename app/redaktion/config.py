"""Settings from ~/.config/bitz-newsletter.json, with overrides for test runs.

REDAKTION_REPO_PATH points the app at another clone of the private repository
(a throwaway copy for testing). REDAKTION_DRY_RUN=1 switches off every step
that leaves the Mac: push, Element ping, issue edits and Buttondown.
"""
import json
import os
import pathlib
from dataclasses import dataclass

CONFIG_PATH = pathlib.Path(os.environ.get("BITZ_CONFIG", "~/.config/bitz-newsletter.json")).expanduser()
BUILD_REPO = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = pathlib.Path(os.environ.get("REDAKTION_DATA", "~/.local/share/bitz-redaktion")).expanduser()
QUARTO_CANDIDATES = [
    os.environ.get("QUARTO_PATH", ""),
    "/Applications/RStudio.app/Contents/Resources/app/quarto/bin/quarto",
    "/usr/local/bin/quarto",
    "/opt/homebrew/bin/quarto",
]


@dataclass
class Config:
    private_repo: str
    repo_path: pathlib.Path
    element_room: str
    app_url: str
    dry_run: bool
    build_repo: pathlib.Path = BUILD_REPO

    @property
    def quarto(self) -> str | None:
        for c in QUARTO_CANDIDATES:
            if c and pathlib.Path(c).exists():
                return c
        return None


def load() -> Config:
    if not CONFIG_PATH.exists():
        raise SystemExit(f"Konfiguration fehlt: {CONFIG_PATH}")
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    for key in ("private_repo", "private_repo_path"):
        if key not in data:
            raise SystemExit(f"Schlüssel fehlt in {CONFIG_PATH}: {key}")
    repo = os.environ.get("REDAKTION_REPO_PATH") or data["private_repo_path"]
    return Config(
        private_repo=data["private_repo"],
        repo_path=pathlib.Path(repo).expanduser(),
        element_room=data.get("element_room", ""),  # unused since 0034
        app_url=data.get("app_url", "http://127.0.0.1:8765"),
        dry_run=os.environ.get("REDAKTION_DRY_RUN") == "1",
    )
