"""Editions and raw drafts, read from the private repository.

The stage of an edition always comes from skills/runner/scripts/stand.py, the
same script the runner reads, so the app and the runner never disagree.
"""
import datetime as dt
import importlib.util
import re
import shutil
from pathlib import Path

import yaml

from .config import BUILD_REPO, Config
from . import gitops

_spec = importlib.util.spec_from_file_location("stand", BUILD_REPO / "skills/runner/scripts/stand.py")
stand = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(stand)

# Board columns: (title, stage ids)
COLUMNS = [
    ("Recherche bis Prüfungen", {"4", "5a", "5b", "6"}),
    ("Grafiken und Übersetzung", {"7", "8"}),
    ("Freigabe", {"9"}),
    ("Versand", {"10"}),
    ("Verbreitung", {"11", "fertig"}),
]

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FOLDER_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(-[a-z0-9]+)*$")


def frontmatter(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return {}


def body_without_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def editions_dir(cfg: Config) -> Path:
    return cfg.repo_path / "ausgaben"


def edition(cfg: Config, name: str) -> dict:
    folder = editions_dir(cfg) / name
    if not FOLDER_RE.match(name):
        raise ValueError(f"kein Ausgabenordner: {name}")
    if not folder.is_dir():
        raise FileNotFoundError(name)
    state = stand.infer(folder)
    meta = frontmatter(folder / "index.qmd")
    title = meta.get("title") or name
    return {
        "name": name,
        "folder": folder,
        "rel": f"ausgaben/{name}",
        "title": title,
        "date": name[:10],
        "meta": meta,
        "state": state,
        "waiting": bool(state["gate_waiting"]) or state["next"]["who"] == "lars",
    }


def list_editions(cfg: Config) -> list[dict]:
    root = editions_dir(cfg)
    if not root.is_dir():
        return []
    return [edition(cfg, p.name) for p in sorted(root.iterdir()) if p.is_dir() and not p.name.startswith("_")]


def board(cfg: Config) -> list[tuple[str, list[dict]]]:
    eds = list_editions(cfg)
    return [(title, [e for e in eds if e["state"]["next"]["id"] in ids]) for title, ids in COLUMNS]


def list_drafts(cfg: Config) -> list[dict]:
    root = cfg.repo_path / "_entwuerfe"
    if not root.is_dir():
        return []
    out = []
    for p in sorted(root.glob("*.md"), reverse=True):
        if p.name.lower() == "readme.md":
            continue
        meta = frontmatter(p)
        body = body_without_frontmatter(p.read_text(encoding="utf-8"))
        out.append({
            "file": p.name,
            "meta": meta,
            "words": len(body.split()),
            "start": " ".join(body.split()[:30]),
        })
    return out


def read_file(cfg: Config, name: str, filename: str) -> str | None:
    folder = editions_dir(cfg) / name
    path = (folder / filename).resolve()
    if folder.resolve() not in path.parents or not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def take_draft(cfg: Config, draft_file: str, send_date: str, short: str) -> tuple[str, str]:
    """Start an edition from a raw draft. Returns (folder name, commit)."""
    dt.date.fromisoformat(send_date)
    if not NAME_RE.match(short):
        raise ValueError("Kurzname nur aus Kleinbuchstaben, Ziffern und Bindestrichen")
    src = cfg.repo_path / "_entwuerfe" / Path(draft_file).name
    if not src.exists():
        raise FileNotFoundError(draft_file)
    name = f"{send_date}-{short}"
    folder = editions_dir(cfg) / name
    if folder.exists():
        raise FileExistsError(name)
    if gitops.current_branch(cfg.repo_path) != "dev":
        raise gitops.GitError("Das private Repository steht nicht auf dev.")

    folder.mkdir(parents=True)
    vorlage = editions_dir(cfg) / "_vorlage" / "index.qmd"
    qmd = vorlage.read_text(encoding="utf-8")
    qmd = qmd.replace('date: "TODO: JJJJ-MM-TT, das Sendedatum"', f'date: "{send_date}"', 1)
    (folder / "index.qmd").write_text(qmd, encoding="utf-8")
    shutil.copyfile(src, folder / "rohentwurf.md")

    rel = f"ausgaben/{name}"
    sha = gitops.commit_paths(
        cfg.repo_path,
        [f"{rel}/index.qmd", f"{rel}/rohentwurf.md"],
        f"feat(ausgabe): {name} aus dem Entwurf {src.name}\n\n"
        f"Ordner aus der Vorlage, Rohentwurf unverändert übernommen.\n\n"
        f"Human-authored: true\n",
    )
    return name, sha


def issue_body(cfg: Config, name: str, send_date: str) -> str:
    """Issue body in the shape of the issue form, with every stage unticked."""
    raw = (editions_dir(cfg) / name / "rohentwurf.md").read_text(encoding="utf-8")
    labels = [s[5] for s in stand.STAGES] + ["12 Frage gestellt, Antworten gesammelt"]
    boxes = "\n".join(f"- [ ] {l}" for l in labels)
    return (
        f"### Sendedatum\n\n{send_date}\n\n"
        f"### Hauptleserschaft\n\nTODO\n\n"
        f"### Rohentwurf\n\n{body_without_frontmatter(raw).strip()}\n\n"
        f"### Stufen und Prüfpunkte\n\n{boxes}\n\n"
        f"Ordner: `ausgaben/{name}/`\n"
    )
