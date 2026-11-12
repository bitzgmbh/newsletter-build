#!/usr/bin/env python3
"""The mechanical part of the ideen skill (decision 0038). Code in English,
output in German, standard library only.

Subcommands, each with --repo (default: private_repo_path from
~/.config/bitz-newsletter.json):

  eingang [--room ID] [--ids 82-85] [--dry-run] [--language auto]
      Every unprocessed row of the ideas room becomes one file in _ideen/,
      then the row is marked processed in archive.db. Audio rows are
      transcribed first with ~/bin/voice_note_insert.py --in-place; the
      voice_notes row is marked processed with its chat row. An edit row
      (replaces set) replaces the text of the idea it edits.
  liste
      The backlog by status: neu, besprochen, gewählt, verworfen.
  status DATEI STATUS [--text TEXT]
      Change the status of an idea and append a line to its Verlauf.
  rohentwurf DATEI --kurzname NAME --titel TITEL [--datum JJJJ-MM-TT] < bullets
      Write _entwuerfe/<datum>-<kurzname>.md from the bullets on stdin and
      mark the idea gewählt.
  notiz --titel TITEL --quelle QUELLE [--datum D] [--form F] [--medien PFAD] < text
      File one idea that did not come through the room.

The script never commits and never writes outside _ideen/ and _entwuerfe/
of the private repository. Run the tests with:
python3 -m unittest discover skills/ideen/tests
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import unicodedata

STATUS = ("neu", "besprochen", "gewählt", "verworfen")
IDEEN = "_ideen"
ENTWUERFE = "_entwuerfe"
DB = pathlib.Path.home() / "archive" / "archive.db"
INSERT = pathlib.Path.home() / "bin" / "voice_note_insert.py"
CONFIG = pathlib.Path(os.environ.get("BITZ_CONFIG", "~/.config/bitz-newsletter.json")).expanduser()
PREFIX = re.compile(r"^\s*newsletter\s*:\s*", re.I)
KURZNAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
UMLAUT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"})
VERLAUF = "## Verlauf"


def today() -> str:
    return dt.date.today().isoformat()


def slug(text: str, words: int = 5, maxlen: int = 40) -> str:
    t = unicodedata.normalize("NFKD", text.translate(UMLAUT)).encode("ascii", "ignore").decode()
    parts = [w for w in re.split(r"[^a-z0-9]+", t.lower()) if w]
    return "-".join(parts[:words])[:maxlen].strip("-") or "idee"


def titel(text: str, words: int = 6, maxlen: int = 60) -> str:
    t = " ".join(" ".join(text.split()).split()[:words]).rstrip(" .,:;!?")
    return t[:maxlen]


def quote(value) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def frontmatter_text(meta: dict) -> str:
    lines = ["---"] + [f"{k}: {quote(v)}" for k, v in meta.items() if v not in (None, "")] + ["---"]
    return "\n".join(lines) + "\n"


def split_frontmatter(text: str):
    """(meta, body) for a file with a simple key: "value" front matter."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[3:end].strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            try:
                value = json.loads(value)
            except ValueError:
                value = value[1:-1]
        meta[key.strip()] = value
    return meta, text[end + 4:].lstrip("\n")


def split_verlauf(body: str):
    """(text, verlauf lines) of an idea body."""
    if VERLAUF in body:
        text, rest = body.split(VERLAUF, 1)
        lines = [ln for ln in rest.strip().splitlines() if ln.strip()]
        return text.rstrip(), lines
    return body.rstrip(), []


def compose(meta: dict, text: str, verlauf: list) -> str:
    return frontmatter_text(meta) + "\n" + text.rstrip() + "\n\n" + VERLAUF + "\n\n" + "\n".join(verlauf) + "\n"


def unique_path(folder: pathlib.Path, stem: str) -> pathlib.Path:
    path, n = folder / f"{stem}.md", 2
    while path.exists():
        path, n = folder / f"{stem}-{n}.md", n + 1
    return path


def idea_files(repo: pathlib.Path):
    folder = repo / IDEEN
    if not folder.is_dir():
        return []
    return [p for p in sorted(folder.glob("*.md")) if p.name.lower() != "readme.md"]


def read_idea(path: pathlib.Path) -> dict:
    meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
    text, verlauf = split_verlauf(body)
    return {"file": path.name, "path": path, "meta": meta, "text": text, "verlauf": verlauf,
            "status": str(meta.get("status", "neu"))}


def write_idea(repo, datum, form, titel_, text, quelle, medien=None, verlauf="abgelegt", when=None):
    folder = repo / IDEEN
    folder.mkdir(exist_ok=True)
    path = unique_path(folder, f"{datum}-{slug(titel_)}")
    meta = {"datum": datum, "status": "neu", "form": form, "titel": titel_, "quelle": quelle}
    if medien:
        meta["medien"] = str(medien)
    path.write_text(compose(meta, text, [f"- {when or today()}: {verlauf}"]), encoding="utf-8")
    return path


def find_by_quelle(repo: pathlib.Path, ref: str):
    for path in idea_files(repo):
        quelle = str(read_idea(path)["meta"].get("quelle", ""))
        if ref in [q.strip() for q in quelle.split(",")]:
            return path
    return None


def replace_text(path: pathlib.Path, text: str, note: str, when=None):
    idea = read_idea(path)
    idea["verlauf"].append(f"- {when or today()}: {note}")
    path.write_text(compose(idea["meta"], text, idea["verlauf"]), encoding="utf-8")


# --- eingang -----------------------------------------------------------------

def parse_ids(spec: str):
    ids = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            ids.extend(range(int(a), int(b) + 1))
        elif part:
            ids.append(int(part))
    return ids


def new_rows(con, room, ids=None):
    query = ("SELECT id, event_id, sent_at, msgtype, body, media_path, replaces FROM chat_messages"
             " WHERE room_id = ? AND processed = 0")
    params = [room]
    if ids:
        query += " AND id IN (%s)" % ",".join("?" * len(ids))
        params += list(ids)
    return con.execute(query + " ORDER BY sent_at, id", params).fetchall()


def voice_row(con, media_path):
    return con.execute("SELECT id, transcript FROM voice_notes WHERE audio_path = ?", (media_path,)).fetchone()


def transcribe(con, media_path, sent_at, language):
    """Default transcriber: the insert script writes the voice_notes row."""
    subprocess.run([sys.executable, str(INSERT), media_path, "--in-place",
                    "--recorded-at", sent_at, "--language", language],
                   check=True, capture_output=True, text=True)


def eingang(db, repo, room, ids=None, dry_run=False, language="auto", transcriber=None, when=None):
    repo = pathlib.Path(repo)
    con = sqlite3.connect(str(db))
    done = []
    for rid, event_id, sent_at, msgtype, body, media_path, replaces in new_rows(con, room, ids):
        datum = (sent_at or when or today())[:10]
        text = PREFIX.sub("", body or "").strip()
        voice_id, medien = None, None
        if msgtype == "m.audio" and media_path:
            form = "gesprochen"
            row = voice_row(con, media_path)
            if row is None and not dry_run:
                (transcriber or transcribe)(con, media_path, sent_at, language)
                row = voice_row(con, media_path)
            if row is None:
                text = "(Sprachnachricht, noch nicht transkribiert)"
            else:
                voice_id, text = row[0], (row[1] or "").strip()
        elif media_path:
            form = "foto" if msgtype == "m.image" else "datei"
            medien = media_path
        else:
            form = "geschrieben"
        quelle = f"archive.db:chat_messages/{rid}"
        if voice_id:
            quelle += f", archive.db:voice_notes/{voice_id}"
        name = titel(text) or (pathlib.Path(media_path).name if media_path else "Idee")
        target = None
        if replaces:
            orig = con.execute("SELECT id FROM chat_messages WHERE event_id = ?", (replaces,)).fetchone()
            if orig:
                target = find_by_quelle(repo, f"archive.db:chat_messages/{orig[0]}")
        if dry_run:
            done.append({"id": rid, "form": form, "titel": name, "file": target.name if target else None,
                         "dry_run": True})
            continue
        if target is not None:
            replace_text(target, text, f"Text ersetzt durch {quelle}", when)
            path = target
        else:
            path = write_idea(repo, datum, form, name, text, quelle, medien=medien,
                              verlauf=f"abgelegt aus dem Raum, {quelle}", when=when)
        con.execute("UPDATE chat_messages SET processed = 1 WHERE id = ?", (rid,))
        if voice_id:
            con.execute("UPDATE voice_notes SET processed = 1 WHERE id = ?", (voice_id,))
        con.commit()
        done.append({"id": rid, "form": form, "titel": name, "file": path.name, "dry_run": False})
    con.close()
    return done


# --- liste, status, rohentwurf, notiz -------------------------------------------

def liste(repo):
    ideas = [read_idea(p) for p in idea_files(pathlib.Path(repo))]
    ideas.sort(key=lambda i: i["file"], reverse=True)
    ideas.sort(key=lambda i: STATUS.index(i["status"]) if i["status"] in STATUS else len(STATUS))
    return ideas


def set_status(repo, file, status, text=None, when=None, extra=None):
    if status not in STATUS:
        raise ValueError("Status muss einer von %s sein, nicht %r" % (", ".join(STATUS), status))
    path = pathlib.Path(repo) / IDEEN / pathlib.Path(file).name
    if not path.exists():
        raise FileNotFoundError(f"Keine Idee {path.name} in {IDEEN}/")
    idea = read_idea(path)
    idea["meta"]["status"] = status
    if extra:
        idea["meta"].update(extra)
    idea["verlauf"].append(f"- {when or today()}: {status}" + (f", {text}" if text else ""))
    path.write_text(compose(idea["meta"], idea["text"], idea["verlauf"]), encoding="utf-8")
    return path


def rohentwurf(repo, file, kurzname, titel_, bullets, datum=None, when=None):
    repo = pathlib.Path(repo)
    if not KURZNAME.match(kurzname):
        raise ValueError("Kurzname: nur Kleinbuchstaben, Ziffern und Bindestriche")
    datum = datum or today()
    folder = repo / ENTWUERFE
    folder.mkdir(exist_ok=True)
    target = folder / f"{datum}-{kurzname}.md"
    if target.exists():
        raise FileExistsError(f"{ENTWUERFE}/{target.name} gibt es schon")
    meta = {"datum": datum, "form": "besprochen", "ausgabe": titel_, "idee": f"{IDEEN}/{pathlib.Path(file).name}"}
    target.write_text(frontmatter_text(meta) + "\n" + bullets.strip() + "\n", encoding="utf-8")
    link = f"{ENTWUERFE}/{target.name}"
    set_status(repo, file, "gewählt", text=f"Rohentwurf {link}", when=when, extra={"entwurf": link})
    return target


def notiz(repo, titel_, quelle, text, datum=None, form="geschrieben", medien=None, when=None):
    return write_idea(pathlib.Path(repo), datum or today(), form, titel_, text, quelle,
                      medien=medien, verlauf=f"abgelegt, Quelle {quelle}", when=when)


# --- command line ---------------------------------------------------------------

def load_config() -> dict:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def main(argv=None):
    cfg = load_config()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=cfg.get("private_repo_path"), help="the private repository")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("eingang")
    e.add_argument("--db", default=str(DB))
    e.add_argument("--room", default=cfg.get("ideas_room_id"))
    e.add_argument("--ids", help="only these row ids, for example 82-85 or 82,84")
    e.add_argument("--dry-run", action="store_true")
    e.add_argument("--language", default="auto")
    sub.add_parser("liste")
    s = sub.add_parser("status")
    s.add_argument("datei")
    s.add_argument("status", choices=STATUS)
    s.add_argument("--text")
    r = sub.add_parser("rohentwurf")
    r.add_argument("datei")
    r.add_argument("--kurzname", required=True)
    r.add_argument("--titel", required=True)
    r.add_argument("--datum")
    n = sub.add_parser("notiz")
    n.add_argument("--titel", required=True)
    n.add_argument("--quelle", required=True)
    n.add_argument("--datum")
    n.add_argument("--form", default="geschrieben", choices=("geschrieben", "gesprochen", "foto", "datei"))
    n.add_argument("--medien")
    args = ap.parse_args(argv)
    if not args.repo:
        ap.error("--repo fehlt und private_repo_path steht nicht in der Konfiguration")
    repo = pathlib.Path(args.repo).expanduser()

    if args.cmd == "eingang":
        if not args.room:
            ap.error("--room fehlt und ideas_room_id steht nicht in der Konfiguration")
        ids = parse_ids(args.ids) if args.ids else None
        done = eingang(args.db, repo, args.room, ids=ids, dry_run=args.dry_run, language=args.language)
        for d in done:
            where = d["file"] or f"{IDEEN}/{d['titel']} (neu)"
            print(("würde ablegen: " if d["dry_run"] else "abgelegt: ") + f"{where}  ({d['form']}, Zeile {d['id']})")
        print(f"{len(done)} {'Zeile' if len(done) == 1 else 'Zeilen'}" + (" (Trockenlauf)" if args.dry_run else ""))
    elif args.cmd == "liste":
        ideas = liste(repo)
        if not ideas:
            print(f"Keine Ideen in {IDEEN}/.")
            return
        for i in ideas:
            m = i["meta"]
            print(f"{i['status']:<11} {m.get('datum', ''):<10} {m.get('form', ''):<11} {m.get('titel', '')}  [{i['file']}]")
        counts = {s: sum(1 for i in ideas if i["status"] == s) for s in STATUS}
        print(", ".join(f"{v} {k}" for k, v in counts.items() if v) + f", {len(ideas)} insgesamt")
    elif args.cmd == "status":
        path = set_status(repo, args.datei, args.status, text=args.text)
        print(f"{IDEEN}/{path.name}: {args.status}")
    elif args.cmd == "rohentwurf":
        bullets = sys.stdin.read()
        if not bullets.strip():
            ap.error("keine Stichpunkte auf stdin")
        target = rohentwurf(repo, args.datei, args.kurzname, args.titel, bullets, datum=args.datum)
        print(f"Rohentwurf {ENTWUERFE}/{target.name}, Idee {args.datei} gewählt")
    elif args.cmd == "notiz":
        text = sys.stdin.read()
        if not text.strip():
            ap.error("kein Text auf stdin")
        path = notiz(repo, args.titel, args.quelle, text, datum=args.datum, form=args.form, medien=args.medien)
        print(f"abgelegt: {IDEEN}/{path.name}")


if __name__ == "__main__":
    main()
