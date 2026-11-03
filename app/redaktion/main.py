"""Routes of the app. Screens in German, code in English.

Every step that moves an edition goes through the runner (runs.py), except
the two buttons that are Lars's alone: Freigabe (stage 9) and Versand
(stage 10, a draft in Buttondown).
"""
import asyncio
import datetime as dt
import json
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote

import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markdown_it import MarkdownIt

from . import buttondown, config, editions, gitops, runs

HERE = Path(__file__).parent
cfg = config.load()
app = FastAPI(title="Redaktion")
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
templates = Jinja2Templates(directory=HERE / "templates")
md = MarkdownIt("commonmark", {"html": False}).enable("table")
templates.env.filters["md"] = lambda text: md.render(text or "")
templates.env.filters["zeit"] = lambda ts: dt.datetime.fromtimestamp(ts).strftime("%d.%m. %H:%M") if ts else ""

OUTPUTS = ["recherche.md", "gliederung.md", "pruefung-stimme.md", "pruefbericht.md", "grafiken.md",
           "verbreitung.md", "rohentwurf.md", "index-en.qmd"]
BACK_TO = ["5b", "5a", "4"]


def page(request: Request, name: str, **ctx):
    ctx.update(request=request, dry_run=cfg.dry_run, repo=cfg.repo_path)
    return templates.TemplateResponse(request, name, ctx)


def load_edition(name: str) -> dict:
    try:
        return editions.edition(cfg, name)
    except (ValueError, FileNotFoundError):
        raise HTTPException(404, f"Keine Ausgabe {name}")


def now() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def append_gate(folder: Path, line: str) -> None:
    pp = folder / "pruefpunkte.md"
    if not pp.exists():
        pp.write_text(
            f"# Prüfpunkte: {folder.name}\n\nEine Zeile pro Prüfpunkt, angehängt, nie umgeschrieben.\n\n",
            encoding="utf-8",
        )
    text = pp.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    pp.write_text(text + f"- {now()} {line}\n", encoding="utf-8")


@app.on_event("startup")
def _startup():
    runs.mark_stale()


@app.get("/", response_class=HTMLResponse)
def uebersicht(request: Request):
    eds = editions.list_editions(cfg)
    return page(
        request, "uebersicht.j2",
        columns=editions.board(cfg),
        drafts=editions.list_drafts(cfg),
        waiting=[e for e in eds if e["waiting"]],
        recent=runs.recent(limit=8),
        active={e["name"]: runs.active(e["name"]) for e in eds},
    )


@app.get("/entwurf/{file}", response_class=HTMLResponse)
def entwurf(request: Request, file: str):
    drafts = {d["file"]: d for d in editions.list_drafts(cfg)}
    if file not in drafts:
        raise HTTPException(404, "Kein Entwurf")
    text = (cfg.repo_path / "_entwuerfe" / file).read_text(encoding="utf-8")
    return page(request, "entwurf.j2", draft=drafts[file], text=editions.body_without_frontmatter(text))


@app.post("/entwurf/{file}")
def entwurf_uebernehmen(file: str, sendedatum: str = Form(...), kurzname: str = Form(...),
                        titel: str = Form("")):
    try:
        name, sha = editions.take_draft(cfg, file, sendedatum, kurzname.strip())
    except (ValueError, FileExistsError, FileNotFoundError, gitops.GitError) as exc:
        raise HTTPException(400, str(exc))
    note = f"Commit {sha} auf dev. "
    note += gitops.push(cfg.repo_path, "dev", cfg.dry_run) + ". "
    if cfg.dry_run:
        note += "Trockenlauf: kein Issue angelegt."
    else:
        body = editions.issue_body(cfg, name, sendedatum)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
            fh.write(body)
        p = subprocess.run(["gh", "issue", "create", "-R", cfg.private_repo, "--title",
                            f"Ausgabe: {titel or name}", "--label", "ausgabe", "--body-file", fh.name],
                           capture_output=True, text=True)
        os.unlink(fh.name)
        note += ("Issue: " + p.stdout.strip()) if p.returncode == 0 else ("Issue nicht angelegt: " + p.stderr.strip())
    return RedirectResponse(f"/ausgabe/{name}?hinweis={quote(note)}", status_code=303)


@app.get("/ausgabe/{name}", response_class=HTMLResponse)
def ausgabe(request: Request, name: str, datei: str | None = None, hinweis: str = ""):
    e = load_edition(name)
    present = [f for f in OUTPUTS if f in e["state"]["files"]]
    shown = datei if datei in present else None
    if not shown:
        waiting = e["state"]["gate_waiting"]
        wanted = editions.stand.BY_ID[waiting][3] if waiting else None
        shown = wanted if wanted in present else (present[0] if present else None)
    qmd = editions.read_file(cfg, name, "index.qmd") or ""
    preview = buttondown.clean_markdown(editions.body_without_frontmatter(qmd), e["meta"], {})
    return page(
        request, "ausgabe.j2", e=e, present=present, shown=shown,
        shown_text=editions.read_file(cfg, name, shown) if shown else "",
        preview=preview, back_to=BACK_TO, hinweis=hinweis,
        active=runs.active(name), recent=runs.recent(name, 5),
    )


@app.post("/ausgabe/{name}/lauf")
def lauf_starten(name: str, aktion: str = Form(...), text: str = Form(""), zurueck: str = Form("5b"),
                 quelle: str = Form("")):
    e = load_edition(name)
    st = e["state"]
    verdict = None
    if aktion == "ja":
        verdict = "ja"
    elif aktion == "geaendert":
        if not text.strip():
            raise HTTPException(400, "Bitte schreib, was sich ändern soll.")
        verdict = 'geändert: "' + text.strip().replace('"', "'") + '"'
    elif aktion == "blockiert":
        if zurueck not in BACK_TO:
            raise HTTPException(400, "Unbekannte Stufe")
        verdict = f"blockiert, zurück zu {zurueck}"
    elif aktion == "text_fertig":
        if st["empty_parts"]:
            raise HTTPException(400, "Noch ohne Text: " + ", ".join(st["empty_parts"]))
    elif aktion != "start":
        raise HTTPException(400, "Unbekannte Aktion")
    if st["next"]["id"] in ("9", "10", "fertig") and not verdict:
        raise HTTPException(400, "Diese Stufe läuft nicht über den Runner.")
    try:
        run_id = runs.start(cfg, name, e["rel"], st["gate_waiting"] or st["next"]["id"], verdict,
                            quelle.strip() or None)
    except RuntimeError as exc:
        raise HTTPException(409, str(exc))
    return RedirectResponse(f"/lauf/{run_id}", status_code=303)


@app.get("/lauf/{run_id}", response_class=HTMLResponse)
def lauf(request: Request, run_id: int):
    r = runs.get(run_id)
    if not r:
        raise HTTPException(404, "Kein Lauf")
    return page(request, "lauf.j2", run=r, events=runs.events_after(run_id, 0))


@app.get("/lauf/{run_id}/events")
async def lauf_events(run_id: int, after: int = 0):
    async def stream():
        last = after
        while True:
            for ev in runs.events_after(run_id, last):
                last = ev["rowid"]
                data = json.dumps({"id": last, "kind": ev["kind"], "text": ev["text"]}, ensure_ascii=False)
                yield f"data: {data}\n\n"
            r = runs.get(run_id)
            if r and r["status"] != "läuft" and not runs.events_after(run_id, last):
                end = {"status": r["status"], "cost": r["cost"], "turns": r["turns"]}
                yield f"event: ende\ndata: {json.dumps(end)}\n\n"
                return
            await asyncio.sleep(0.7)
    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/ausgabe/{name}/freigabe", response_class=HTMLResponse)
def freigabe(request: Request, name: str, hinweis: str = ""):
    e = load_edition(name)
    preview = gitops.freigabe_preview(cfg.repo_path, e["rel"])
    return page(request, "freigabe.j2", e=e, p=preview, branch=gitops.current_branch(cfg.repo_path),
                hinweis=hinweis)


@app.post("/ausgabe/{name}/freigabe")
def freigeben(name: str, bestaetigt: str = Form("")):
    e = load_edition(name)
    if e["state"]["next"]["id"] != "9":
        raise HTTPException(400, "Die Ausgabe steht nicht bei Stufe 9.")
    if bestaetigt != "ja":
        raise HTTPException(400, "Bitte bestätigen.")
    repo = cfg.repo_path
    if gitops.current_branch(repo) != "dev":
        raise HTTPException(400, "Das private Repository steht nicht auf dev.")
    pre = gitops.freigabe_preview(repo, e["rel"])
    if not pre["fast_forward"]:
        raise HTTPException(400, f"{pre['base']} hat Commits, die dev nicht hat. Erst main in dev mergen.")
    steps = []
    off = subprocess.run(["Rscript", str(cfg.build_repo / "skills/offenlegung/offenlegung.R"), e["rel"],
                          "--schreiben"], cwd=repo, capture_output=True, text=True)
    steps.append("Offenlegung geschrieben" if off.returncode == 0 else
                 "Offenlegung nicht geschrieben: " + (off.stderr or off.stdout)[-300:])
    append_gate(e["folder"], "Stufe 9 Freigabe: ja (Knopf in der App)")
    sha = gitops.commit_paths(repo, [f"{e['rel']}/index.qmd", f"{e['rel']}/pruefpunkte.md"],
                              f"chore(ausgabe): Freigabe {name}\n\nHuman-authored: true\n")
    steps.append(f"Commit {sha}")
    steps.append(gitops.push(repo, "dev", cfg.dry_run))
    steps.append(gitops.push(repo, "dev:main", cfg.dry_run))
    gitops.git(repo, "fetch", "-q", ".", "dev:main")
    steps.append("main lokal auf dev, dev enthält main")
    return RedirectResponse(f"/ausgabe/{name}/versand?hinweis={quote('. '.join(steps))}", status_code=303)


def _versand_data(e: dict, lang: str):
    qmd = "index.qmd" if lang == "de" else "index-en.qmd"
    if not (e["folder"] / qmd).exists():
        return None
    meta, body, root = buttondown.render(cfg, e["folder"], qmd)
    return {"lang": lang, "qmd": qmd, "meta": meta, "body": body, "root": root,
            "problems": buttondown.check_fields(meta), "images": buttondown.local_images(body)}


@app.get("/ausgabe/{name}/versand", response_class=HTMLResponse)
def versand(request: Request, name: str, hinweis: str = ""):
    e = load_edition(name)
    items, errors = [], []
    for lang in ("de", "en"):
        try:
            d = _versand_data(e, lang)
            if d:
                items.append(d)
        except buttondown.VersandError as exc:
            errors.append(f"{lang}: {exc}")
    return page(request, "versand.j2", e=e, items=items, errors=errors, hinweis=hinweis)


@app.post("/ausgabe/{name}/versand")
def versand_entwurf(name: str, sprache: str = Form("de")):
    e = load_edition(name)
    if e["state"]["next"]["id"] not in ("10", "11", "fertig"):
        raise HTTPException(400, "Erst die Freigabe (Stufe 9).")
    try:
        d = _versand_data(e, sprache)
        if not d:
            raise buttondown.VersandError("Keine Datei für diese Sprache.")
        if d["problems"]:
            raise buttondown.VersandError("; ".join(d["problems"]))
        if cfg.dry_run:
            result = {"id": "trockenlauf", "url": ""}
        else:
            result = buttondown.create_draft(d["meta"], d["body"], d["root"])
    except buttondown.VersandError as exc:
        raise HTTPException(400, str(exc))
    label = "" if sprache == "de" else " (englisch)"
    append_gate(e["folder"], f"Stufe 10 Versand: Entwurf in Buttondown{label} {result['id']}")
    sha = gitops.commit_paths(cfg.repo_path, [f"{e['rel']}/pruefpunkte.md"],
                              f"chore(ausgabe): Buttondown Entwurf {name}{label}\n\nHuman-authored: true\n")
    gitops.push(cfg.repo_path, "dev", cfg.dry_run)
    note = f"Entwurf {result['id']} angelegt, Commit {sha}. Jetzt in Buttondown prüfen und senden."
    if result["url"]:
        note += " " + result["url"]
    return RedirectResponse(f"/ausgabe/{name}/versand?hinweis={quote(note)}", status_code=303)


def run():
    port = int(os.environ.get("REDAKTION_PORT", "8765"))
    uvicorn.run("redaktion.main:app", host="127.0.0.1", port=port, reload=False)
