"""The Buttondown draft of an edition from the terminal (stage 10, decision 0037).

Usage, from app/:
  uv run python -m redaktion.entwurf pruefen <edition> [--en]
  uv run python -m redaktion.entwurf aktualisieren <edition> [--en]
  uv run python -m redaktion.entwurf publikum <edition> [--en]
  uv run python -m redaktion.entwurf nummer <edition> <number> [--en]

The draft is created once through the app (POST /ausgabe/<name>/versand), which
writes its id into pruefpunkte.md. These commands work on that draft:

  pruefen        reads the draft back from Buttondown and checks it
  aktualisieren  renders the edition again, uploads the figures, replaces the
                 body, subject and preview line of the draft, then checks it
  publikum       sets the audience by the answer to the language question (0036)
  nummer         sets the issue number; German and English carry the same one

Never sends. Exit 0 when every check passes, 2 when one fails, 1 on usage error.
"""
import re
import sys

import httpx

from . import buttondown, config
from .editions import edition

MARKER = "<!-- buttondown-editor-mode: plaintext -->"
SPRACHE = "subscriber.metadata.sprache"


def draft_id(folder, en: bool) -> str:
    """The id in the last 'Stufe 10 Versand' line of pruefpunkte.md for this language."""
    found = ""
    for line in (folder / "pruefpunkte.md").read_text(encoding="utf-8").splitlines():
        m = re.search(r"Stufe 10 Versand: Entwurf in Buttondown( \(englisch\))? (em_\w+)", line)
        if m and bool(m.group(1)) == en:
            found = m.group(2)
    if not found:
        raise SystemExit("Kein Entwurf in pruefpunkte.md. Zuerst über die App anlegen (POST /ausgabe/<name>/versand).")
    return found


def audience(en: bool) -> dict:
    """German: deutsch, beide-both and no answer. English: english, beide-both and no answer.
    No answer is the two test accounts from before the language question."""
    values = ["english", "beide-both"] if en else ["deutsch", "beide-both"]
    filters = [{"field": SPRACHE, "operator": "equals", "value": v} for v in values]
    filters.append({"field": SPRACHE, "operator": "is_empty", "value": ""})
    return {"filters": filters, "groups": [], "predicate": "or"}


def checks(d: dict, meta: dict) -> list[tuple[bool, str]]:
    b = d.get("body", "")
    text = re.sub(r"<!--.*?-->", "", b, flags=re.S)
    blocks = [x.strip() for x in text.split("\n\n") if x.strip()]
    wrapped = [x[:40] for x in blocks if "\n" in x and not x.startswith(("- ", "* ", "|", "#"))]
    n_filters = len((d.get("filters") or {}).get("filters", []))
    return [
        (d.get("status") == "draft", f"Status {d.get('status')} (erwartet draft)"),
        (b.startswith(MARKER), "Markdown Modus: der Text beginnt mit der Zeile für den Plaintext Editor"),
        ("<br" not in b and "</p>" not in b, "kein HTML aus dem Rich Text Editor (<br>, <p>)"),
        (not wrapped, f"kein Zeilenende mitten im Absatz {wrapped[:3] if wrapped else ''}".strip()),
        (not buttondown.local_images(b) and "<img" not in b, "Grafiken hochgeladen, kein lokaler Pfad"),
        ("```" not in b and "library(" not in b, "kein Code im Text"),
        ("TODO" not in b and "{{<" not in b, "kein TODO, kein offener Shortcode"),
        (d.get("subject") == str(meta.get("subtitle")), f"Betreff: {d.get('subject')}"),
        (d.get("description") == str(meta.get("description") or ""), "Vorschausatz wie im Kopf der Ausgabe"),
        (n_filters > 0, f"Publikum gefiltert ({n_filters} Bedingungen)"),
    ]


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    number = None
    if len(args) == 3 and args[0] == "nummer" and args[2].isdigit():
        number = int(args.pop())
    if len(args) != 2 or args[0] not in ("pruefen", "aktualisieren", "publikum", "nummer") or (args[0] == "nummer") != (number is not None):
        print(__doc__)
        return 1
    command, name = args
    en = "--en" in argv
    cfg = config.load()
    e = edition(cfg, name)
    qmd = "index-en.qmd" if en else "index.qmd"
    eid = draft_id(e["folder"], en)
    head = {"Authorization": f"Token {buttondown.api_key()}"}
    url = f"{buttondown.API}/emails/{eid}"

    if command == "nummer":
        r = httpx.patch(url, headers=head, json={"secondary_id": number}, timeout=60)
        r.raise_for_status()
        print(f"Nummer {number} gesetzt für {eid}.")
    if command == "publikum":
        r = httpx.patch(url, headers=head, json={"filters": audience(en)}, timeout=60)
        r.raise_for_status()
        print(f"Publikum gesetzt für {eid}.")
    if command == "aktualisieren":
        meta, body, root = buttondown.render(cfg, e["folder"], qmd)
        body = buttondown.upload_images(body, root, head["Authorization"].split(" ", 1)[1])
        r = httpx.patch(url, headers=head, timeout=60, json={
            "subject": str(meta["subtitle"]), "description": str(meta.get("description") or ""),
            "body": MARKER + "\n" + body})
        r.raise_for_status()
        print(f"Entwurf {eid} aktualisiert.")

    d = httpx.get(url, headers=head, timeout=60).json()
    if command != "aktualisieren":
        meta = buttondown._split((e["folder"] / qmd).read_text(encoding="utf-8"))[0]
    failed = 0
    for ok, label in checks(d, meta):
        failed += 0 if ok else 1
        print(("ok    " if ok else "FAIL  ") + label)
    print(f"Zuletzt geändert in Buttondown: {d.get('modification_date')}  https://buttondown.com/emails/{eid}")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
