"""Routes of the app. Screens in German, code in English.

Every step that moves an edition goes through the runner (runs.py), except
the two buttons that are Lars's alone: Freigabe (stage 9) and Versand
(stage 10, a draft in Buttondown).
"""
import asyncio
import datetime as dt
import json
import re
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

from . import bericht, buttondown, config, editions, gitops, punkte, runs

HERE = Path(__file__).parent
cfg = config.load()
app = FastAPI(title="Redaktion")
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
templates = Jinja2Templates(directory=HERE / "templates")
md = MarkdownIt("commonmark", {"html": False}).enable("table")
templates.env.filters["md"] = lambda text: md.render(text or "")
templates.env.filters["zeit"] = lambda ts: dt.datetime.fromtimestamp(ts).strftime("%d.%m. %H:%M") if ts else ""

# The files of an edition in stage order, with the label of their tab.
TABS = {
    "rohentwurf.md": "3 Rohentwurf",
    "recherche.md": "4 Recherche",
    "gliederung.md": "5a Gliederung",
    "index.qmd": "5b Text",
    "pruefung-stimme.md": "5c Prüfung stimme",
    "pruefbericht.md": "6 Prüfbericht",
    "grafiken.md": "7 Grafiken",
    "index-en.qmd": "8 Englisch",
    "verbreitung.md": "11 Verbreitung",
}
OUTPUTS = list(TABS)
OPEN_POINT = re.compile(r"<!--\s*\?\s*(.*?)\s*-->", re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)


def show_qmd(text: str) -> str:
    """index.qmd for reading: subject and preview from the front matter on top,
    open points visible, other comments gone, meta shortcodes filled in."""
    import yaml
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            meta = yaml.safe_load(text[3:end]) or {}
    body = editions.body_without_frontmatter(text)
    body = OPEN_POINT.sub(lambda m: "> **? " + " ".join(m.group(1).split()) + "**", body)
    body = COMMENT.sub("", body)
    body = re.sub(r"\{\{<\s*meta\s+(\w+)\s*>\}\}", lambda m: str(meta.get(m.group(1), "")), body)
    head = (f"**Betreff:** {meta.get('subtitle', '')}\n\n"
            f"**Vorschau:** {meta.get('description', '')}\n\n---\n\n")
    return head + body


POSITRON_BACKUPS = Path.home() / "Library" / "Application Support" / "Positron" / "Backups"


def unsaved_in_positron(e: dict) -> list[str]:
    """Files of the edition with unsaved changes in Positron (its hot exit backups)."""
    prefix = "file://" + str(e["folder"]) + "/"
    names = []
    for f in POSITRON_BACKUPS.glob("*/file/*"):
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                first = fh.readline()
        except OSError:
            continue
        if first.startswith(prefix):
            names.append(first[len(prefix):].split(" ", 1)[0])
    return sorted(set(names))


def refuse_if_unsaved(e: dict) -> None:
    names = unsaved_in_positron(e)
    if names:
        raise HTTPException(409, "Positron hat ungespeicherte Änderungen an " + ", ".join(names)
                            + ". Erst dort speichern (Cmd+S), dann noch einmal klicken.")


def commit_own_edits(e: dict) -> str | None:
    """Lars's own edits to index.qmd at gate 5b are committed as his before the runner runs."""
    rel = f"{e['rel']}/index.qmd"
    if not gitops.git(cfg.repo_path, "status", "--porcelain", "--", rel).strip():
        return None
    return gitops.commit_paths(cfg.repo_path, [rel], (
        f"docs(ausgabe): eigene Änderungen am Text, {e['name']}\n\n"
        "Von Lars in index.qmd geändert, bei der Durchsicht an Prüfpunkt 5b (0032).\n\n"
        "Human-authored: true"))
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
        if not wanted and e["state"]["next"]["id"] == "5b":
            wanted = "gliederung.md"  # the text is not written yet; the outline is what there is
        shown = wanted if wanted in present else (present[0] if present else None)
    qmd = editions.read_file(cfg, name, "index.qmd") or ""
    preview = buttondown.clean_markdown(editions.body_without_frontmatter(qmd), e["meta"], {})
    return page(
        request, "ausgabe.j2", e=e, present=present, shown=shown,
        shown_text=(show_qmd(editions.read_file(cfg, name, shown) or "") if shown and shown.endswith(".qmd")
                    else editions.read_file(cfg, name, shown) if shown else ""),
        preview=preview, back_to=BACK_TO, hinweis=hinweis,
        active=runs.active(name), recent=runs.recent(name, 5),
        qmd_path=e["folder"] / "index.qmd",
        points=_points_for(e, shown),
        report=bericht.parse(editions.read_file(cfg, name, shown) or "") if shown == "pruefbericht.md" else None,
        report6=(bericht.parse(editions.read_file(cfg, name, "pruefbericht.md") or "")
                 if e["state"]["gate_waiting"] == "6" else None),
        gate_rows=[gate_row(g) for g in e["state"]["gates"]],
        unsaved=unsaved_in_positron(e),
        tabs=TABS,
    )


def _points_for(e: dict, shown: str | None) -> list[dict]:
    """Open points of the result whose gate waits; none when another file is shown."""
    waiting = e["state"]["gate_waiting"]
    if not waiting or not shown or shown != editions.stand.BY_ID[waiting][3]:
        return []
    return points_of(shown, editions.read_file(cfg, e["name"], shown) or "")


GATE_LINE = re.compile(r"^- (\S+ \S+) Stufe (\S+) ([^:]+):\s*(.*)$")


def gate_row(line: str) -> dict:
    """One line of pruefpunkte.md, split for the short list: when, stage, verdict word, the rest."""
    m = GATE_LINE.match(line)
    if not m:
        return {"when": "", "stage": "", "word": line[2:], "rest": ""}
    when, stage, name, verdict = m.groups()
    word = re.match(r"(ja, mit Änderungen|ja|geändert|blockiert|offen)?", verdict).group(1) or verdict[:40]
    return {"when": when, "stage": f"{stage} {name.strip()}", "word": word,
            "rest": verdict[len(word):].lstrip(":, ").strip()}


def points_of(filename: str, text: str) -> list[dict]:
    """The check report has its own points (Fail and 'mit Hinweis'); other files mark them with '?'."""
    if filename == "pruefbericht.md":
        return bericht.open_points(text)
    return punkte.open_points(text)


@app.post("/ausgabe/{name}/antworten")
async def antworten(name: str, request: Request):
    """Lars's answers to the open points go to the runner as one 'geändert' verdict."""
    e = load_edition(name)
    waiting = e["state"]["gate_waiting"]
    if not waiting:
        raise HTTPException(400, "Kein Prüfpunkt wartet.")
    filename = editions.stand.BY_ID[waiting][3]
    form = await request.form()
    points = points_of(filename, editions.read_file(cfg, name, filename) or "")
    answers = {}
    for p in points:
        answers[p["n"]] = str(form.get(f"antwort_{p['n']}", ""))
    target = "index.qmd (Befunde aus pruefbericht.md)" if filename == "pruefbericht.md" else filename
    text = punkte.feedback(target, points, answers, str(form.get("allgemein", "")))
    if not text:
        raise HTTPException(400, "Keine Antwort eingetragen.")
    refuse_if_unsaved(e)
    if waiting == "5b":
        commit_own_edits(e)
    try:
        kind = "ja, mit Änderungen" if form.get("weiter") == "ja" else "geändert"
        run_id = runs.start(cfg, name, e["rel"], waiting, f'{kind}: "{text}"')
    except RuntimeError as exc:
        raise HTTPException(409, str(exc))
    return RedirectResponse(f"/lauf/{run_id}", status_code=303)


@app.post("/ausgabe/{name}/oeffnen")
def oeffnen(name: str, datei: str = Form("index.qmd")):
    """Open a file of the edition in Positron (or the default app when Positron is missing)."""
    e = load_edition(name)
    if datei not in ("index.qmd", "index-en.qmd", "rohentwurf.md"):
        raise HTTPException(400, "Diese Datei öffnet die App nicht.")
    path = e["folder"] / datei
    if not path.exists():
        raise HTTPException(404, f"{datei} gibt es noch nicht.")
    app_name = os.environ.get("REDAKTION_EDITOR", "Positron")
    p = subprocess.run(["open", "-a", app_name, str(path)], capture_output=True, text=True)
    if p.returncode != 0:
        subprocess.run(["open", str(path)])
    return RedirectResponse(f"/ausgabe/{name}?hinweis={quote(datei + ' geöffnet in ' + app_name)}",
                            status_code=303)


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
    elif aktion != "start":
        raise HTTPException(400, "Unbekannte Aktion")
    if st["next"]["id"] in ("9", "10", "fertig") and not verdict:
        raise HTTPException(400, "Diese Stufe läuft nicht über den Runner.")
    refuse_if_unsaved(e)
    if st["gate_waiting"] == "5b":
        commit_own_edits(e)
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
    events, texts = [], set()
    for ev in runs.events_after(run_id, 0):
        # older runs logged the final report twice (last text and result)
        if ev["kind"] == "result" and ev["text"].strip() in texts:
            continue
        if ev["kind"] == "text":
            texts.add(ev["text"].strip())
        events.append(ev)
    return page(request, "lauf.j2", run=r, events=events)


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


# JSON for the redaktion skill in Claude Code (decision 0034). It reads the
# same state and open points as the pages and starts runs the same way.

def resolve(name: str) -> str:
    """A full folder name, or its short name without the date."""
    names = [e["name"] for e in editions.list_editions(cfg)]
    if name in names:
        return name
    hits = [n for n in names if n[11:] == name or name in n]
    if len(hits) == 1:
        return hits[0]
    raise HTTPException(404, f"Keine eindeutige Ausgabe für {name}: {', '.join(hits) or 'keine'}")


def summary(e: dict) -> dict:
    st = e["state"]
    return {"name": e["name"], "title": e["title"], "date": e["date"],
            "next": st["next"]["id"], "next_name": st["next"]["name"],
            "gate_waiting": st["gate_waiting"], "active": runs.active(e["name"])}


@app.get("/api/ausgaben")
def api_ausgaben():
    return sorted((summary(e) for e in editions.list_editions(cfg)), key=lambda s: s["date"])


@app.get("/api/ausgabe/{name}")
def api_ausgabe(name: str):
    e = load_edition(resolve(name))
    st = e["state"]
    waiting = st["gate_waiting"]
    datei = editions.stand.BY_ID[waiting][3] if waiting else None
    text = editions.read_file(cfg, e["name"], datei) if datei else ""
    out = summary(e) | {
        "gate_name": editions.stand.BY_ID[waiting][1] if waiting else None,
        "datei": datei, "tab": TABS.get(datei) if datei else None,
        "link": f"{cfg.app_url}/ausgabe/{e['name']}" + (f"?datei={datei}" if datei else ""),
        "punkte": points_of(datei, text or "") if datei else [],
        "unsaved": unsaved_in_positron(e),
        "files": st["files"],
        "gates": [gate_row(g) for g in st["gates"]][-5:],
    }
    if datei == "pruefbericht.md":
        rep_ = bericht.parse(text or "")
        out["bericht"] = {"urteil": rep_["urteil"], "blockiert": rep_["blockiert"],
                          "hart": [{"name": g["name"], "counts": g["counts"]} for g in rep_["hart"]]}
    return out


@app.post("/api/ausgabe/{name}/urteil")
async def api_urteil(name: str, request: Request):
    """Body: {"art": "ja" | "geändert" | "ja, mit Änderungen" | "blockiert", "text": "...", "zurueck": "5b"}."""
    e = load_edition(resolve(name))
    body = await request.json()
    art, text = body.get("art"), " ".join(str(body.get("text", "")).replace('"', "'").split())
    waiting = e["state"]["gate_waiting"]
    if not waiting:
        raise HTTPException(400, "Kein Prüfpunkt wartet.")
    if art == "ja":
        verdict = "ja"
    elif art in ("geändert", "ja, mit Änderungen"):
        if not text:
            raise HTTPException(400, "Text fehlt.")
        verdict = f'{art}: "{text}"'
    elif art == "blockiert" and body.get("zurueck") in BACK_TO:
        verdict = f"blockiert, zurück zu {body['zurueck']}"
    else:
        raise HTTPException(400, "Unbekanntes Urteil.")
    refuse_if_unsaved(e)
    if waiting == "5b":
        commit_own_edits(e)
    try:
        run_id = runs.start(cfg, e["name"], e["rel"], waiting, verdict)
    except RuntimeError as exc:
        raise HTTPException(409, str(exc))
    return {"run_id": run_id, "link": f"{cfg.app_url}/lauf/{run_id}", "verdict": verdict}


@app.get("/api/lauf/{run_id}")
def api_lauf(run_id: int):
    r = runs.get(run_id)
    if not r:
        raise HTTPException(404, "Kein Lauf")
    return {k: r[k] for k in ("id", "edition", "stage", "verdict", "status", "cost", "turns", "result")}


def run():
    port = int(os.environ.get("REDAKTION_PORT", "8765"))
    uvicorn.run("redaktion.main:app", host="127.0.0.1", port=port, reload=False)
