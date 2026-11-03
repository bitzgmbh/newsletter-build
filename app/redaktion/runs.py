"""Headless Claude Code runs of the runner, with a log the page can stream.

One run at a time per edition. The run history lives in a SQLite file outside
git (config.DATA_DIR); the repository stays the record of the pipeline.
"""
import json
import os
import sqlite3
import subprocess
import threading
import time
import uuid
from pathlib import Path

from .config import DATA_DIR, Config

DB = DATA_DIR / "runs.db"
_lock = threading.Lock()
_active: dict[str, int] = {}

STRIP_ENV = [
    "CLAUDECODE", "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_MESSAGING_TOKEN",
    "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_BRIDGE_SESSION_ID",
    "CLAUDE_CODE_SESSION_ID", "CLAUDE_PID", "CLAUDE_CODE_ENTRYPOINT",
]


def db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript("""
        create table if not exists runs (
            id integer primary key, edition text, stage text, verdict text,
            session_id text, started real, ended real, status text,
            cost real, turns integer, result text);
        create table if not exists events (
            run_id integer, seq integer, kind text, text text, at real);
    """)
    return con


def prompt_for(cfg: Config, rel_folder: str, verdict: str | None, quelle: str | None) -> str:
    skill = cfg.build_repo / "skills" / "runner" / "SKILL.md"
    lines = [
        f"Follow the runner skill in {skill} for the edition folder {rel_folder}.",
        "Read that SKILL.md first and the SKILL.md of the stage it names; the stage skills live next to it in "
        f"{cfg.build_repo / 'skills'}.",
    ]
    if verdict:
        lines.append(f"Verdict from Lars for the open gate, clicked in the app: {verdict}")
    else:
        lines.append("No verdict given: there is no open gate, run the next stage.")
    if quelle:
        lines.append(f'--quelle "{quelle}"')
    if cfg.dry_run:
        lines.append(
            "Trockenlauf: commit locally on dev, but do not push, do not send the Element ping and do not "
            "edit the GitHub issue. Print the ping you would have sent."
        )
    lines.append("You run headless: nobody can answer questions. If something is unclear, stop and say what.")
    return "\n".join(lines)


def active(edition: str) -> int | None:
    return _active.get(edition)


def start(cfg: Config, edition: str, rel_folder: str, stage: str,
          verdict: str | None = None, quelle: str | None = None) -> int:
    with _lock:
        if edition in _active:
            raise RuntimeError("Für diese Ausgabe läuft schon eine Stufe.")
        con = db()
        session = str(uuid.uuid4())
        cur = con.execute(
            "insert into runs (edition, stage, verdict, session_id, started, status) values (?,?,?,?,?,?)",
            (edition, stage, verdict or "", session, time.time(), "läuft"),
        )
        con.commit()
        run_id = cur.lastrowid
        _active[edition] = run_id
    prompt = prompt_for(cfg, rel_folder, verdict, quelle)
    t = threading.Thread(target=_run, args=(cfg, edition, run_id, session, prompt), daemon=True)
    t.start()
    return run_id


def _event(con, run_id, seq, kind, text):
    con.execute("insert into events values (?,?,?,?,?)", (run_id, seq, kind, text, time.time()))
    con.commit()


def _summarise_tool(block: dict) -> str:
    name = block.get("name", "?")
    inp = block.get("input") or {}
    for key in ("command", "file_path", "path", "pattern", "url", "description"):
        if key in inp:
            return f"{name}: {str(inp[key])[:200]}"
    return name


def _run(cfg: Config, edition: str, run_id: int, session: str, prompt: str) -> None:
    con = db()
    env = {k: v for k, v in os.environ.items() if k not in STRIP_ENV}
    cmd = [
        os.environ.get("REDAKTION_CLAUDE", "claude"), "-p", prompt,
        "--session-id", session, "--permission-mode", "auto",
        "--output-format", "stream-json", "--verbose",
        "--add-dir", str(cfg.build_repo),
    ]
    seq = 0
    status, cost, turns, result = "fehler", None, None, ""
    _event(con, run_id, seq, "start", prompt)
    try:
        proc = subprocess.Popen(cmd, cwd=cfg.repo_path, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            seq += 1
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                _event(con, run_id, seq, "raw", line[:500])
                continue
            kind = ev.get("type")
            if kind == "assistant":
                for block in ev.get("message", {}).get("content", []):
                    if block.get("type") == "text" and block.get("text", "").strip():
                        _event(con, run_id, seq, "text", block["text"])
                    elif block.get("type") == "tool_use":
                        _event(con, run_id, seq, "tool", _summarise_tool(block))
            elif kind == "result":
                cost = ev.get("total_cost_usd")
                turns = ev.get("num_turns")
                result = ev.get("result") or ""
                status = "fehler" if ev.get("is_error") else "fertig"
                _event(con, run_id, seq, "result", result)
        proc.wait()
        if proc.returncode != 0 and status == "fertig":
            status = "fehler"
    except Exception as exc:  # the page shows it; the run must not hang
        seq += 1
        _event(con, run_id, seq, "raw", f"Fehler beim Start: {exc}")
    finally:
        con.execute("update runs set ended=?, status=?, cost=?, turns=?, result=? where id=?",
                    (time.time(), status, cost, turns, result, run_id))
        con.commit()
        with _lock:
            _active.pop(edition, None)


def get(run_id: int) -> sqlite3.Row | None:
    return db().execute("select * from runs where id=?", (run_id,)).fetchone()


def recent(edition: str | None = None, limit: int = 10) -> list[sqlite3.Row]:
    con = db()
    if edition:
        return con.execute("select * from runs where edition=? order by id desc limit ?", (edition, limit)).fetchall()
    return con.execute("select * from runs order by id desc limit ?", (limit,)).fetchall()


def events_after(run_id: int, after: int) -> list[sqlite3.Row]:
    return db().execute(
        "select rowid, * from events where run_id=? and rowid>? order by rowid", (run_id, after)
    ).fetchall()


def mark_stale() -> None:
    """Runs still 'läuft' from an earlier start of the app did not finish."""
    con = db()
    con.execute("update runs set status='abgebrochen' where status='läuft'")
    con.commit()
