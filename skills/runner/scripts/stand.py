#!/usr/bin/env python3
"""Print where an edition stands in the pipeline.

Usage: stand.py [--json] <edition folder>

Infers the next stage from the files in the folder and from pruefpunkte.md,
lists the files present, and prints the last three gate lines. With --json it
prints the same facts as one JSON object for the app (app/ in this repository).

STAGES below is the one place that names the stages, the issue checkbox labels
and whether a stage ends with a gate.
"""
import json
import pathlib
import re
import sys

# Offengelegt is written by the offenlegung script before stage 9, not at 5b.
PARTS_OPTIONAL = {"Was ihr letztes Mal gesagt habt", "Offengelegt"}

# id, name, who runs it, output file (None when the stage has no file),
# gate after the stage, label of the checkbox in the edition issue
STAGES = [
    ("4", "Recherche", "agent", "recherche.md", True, "4 Recherche"),
    ("5a", "Gliederung", "agent", "gliederung.md", True, "5 Gliederung vom Agenten"),
    ("5b", "Text", "agent", "index.qmd", True, "5 Text vom Agenten, Durchsicht von mir"),
    ("6", "Prüfungen", "agent", "pruefbericht.md", True, "6 Prüfungen"),
    ("7", "Grafiken", "agent", "grafiken.md", True, "7 Grafiken"),
    ("8", "Übersetzung", "agent", "index-en.qmd", True, "8 Übersetzung"),
    ("9", "Freigabe", "lars", None, False, "9 Freigabe (Merge in main)"),
    ("10", "Versand", "lars", None, False, "10 Versand"),
    ("11", "Verbreitung", "agent", "verbreitung.md", True, "11 Verbreitung"),
]
STAGE_IDS = [s[0] for s in STAGES]
BY_ID = {s[0]: s for s in STAGES}


def parts_with_text(qmd):
    text = qmd.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"(?m)^\*Reihe:.*$", "", text)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"\{\{<.*?>\}\}", "", text)
    name, buf, out = "Einstieg", [], {}
    for line in text.splitlines():
        if line.startswith("## "):
            out[name] = len(" ".join(buf).split())
            name, buf = line[3:].strip(), []
        elif not line.startswith("#"):
            buf.append(line)
    out[name] = len(" ".join(buf).split())
    return out


def stage_lines(gates, stage_id):
    pattern = re.compile(r"Stufe " + re.escape(stage_id) + r"\b")
    return [g for g in gates if pattern.search(g)]


def verdict(line, stage_id):
    """The first word after the stage name: ja, geändert, blockiert, offen.

    Only that word counts; the answers in a "geändert" line may say "ja" too.
    """
    m = re.search(r"Stufe " + re.escape(stage_id) + r"\b[^:]*:\s*(\w+)", line)
    return m.group(1) if m else None


def has_yes(gates, stage_id):
    """True when pruefpunkte.md has a 'ja' line for this stage."""
    return any(verdict(g, stage_id) == "ja" for g in stage_lines(gates, stage_id))


def settled(gates, stage_id):
    """True when the gate of this stage has a yes or sent the edition back."""
    return any(verdict(g, stage_id) in ("ja", "blockiert") for g in stage_lines(gates, stage_id))


def infer(folder):
    """Return the state of an edition folder as a dict."""
    have = {p.name for p in folder.iterdir() if p.is_file()}
    gates = []
    pp = folder / "pruefpunkte.md"
    if pp.exists():
        gates = [l for l in pp.read_text(encoding="utf-8").splitlines() if l.startswith("- ")]
    last = gates[-1] if gates else ""
    empty = []
    note = ""

    if "recherche.md" not in have:
        stage = "4"
    elif "gliederung.md" not in have:
        stage = "5a"
    elif "pruefbericht.md" not in have:
        # 5c (the stimme check) is part of 5b since decision 0033: once the
        # text is written, gate 5b waits, then stage 6 runs.
        counts = parts_with_text(folder / "index.qmd") if "index.qmd" in have else {}
        empty = [n for n, c in counts.items() if c == 0 and n not in PARTS_OPTIONAL]
        stage = "5b" if (not counts or empty) else "6"
    elif "zurück zu 5b" in last:
        stage, note = "5b", "nach blockiertem Urteil"
        if "index.qmd" in have:
            counts = parts_with_text(folder / "index.qmd")
            empty = [n for n, c in counts.items() if c == 0 and n not in PARTS_OPTIONAL]
    elif not has_yes(gates, "7"):
        stage = "7"
    elif not has_yes(gates, "8"):
        stage = "8"
    elif not has_yes(gates, "9"):
        stage = "9"
    elif not stage_lines(gates, "10"):
        stage = "10"
    elif not has_yes(gates, "11"):
        stage = "11"
    else:
        stage = "fertig"

    info = BY_ID.get(stage)
    output = info[3] if info else None

    # A gate waits when a stage's output is there and its gate has neither a
    # yes nor a "blockiert". For 7, 8 and 11 that is the next stage itself
    # (the order only moves on after the yes); for 4 to 6 the file order has
    # already moved on, so it is the agent stage just before the next one.
    waiting = None
    # index.qmd exists from the template on, so 5b never waits on itself.
    if info and info[4] and stage != "5b" and output in have and not settled(gates, stage):
        waiting = stage
    elif info and not note:
        idx = STAGE_IDS.index(stage)
        prev = next((s for s in reversed(STAGES[:idx]) if s[2] == "agent"), None)
        if prev and prev[4] and prev[3] in have and not settled(gates, prev[0]):
            waiting = prev[0]

    return {
        "folder": str(folder),
        "files": sorted(have),
        "next": {
            "id": stage,
            "name": info[1] if info else "fertig",
            "who": info[2] if info else None,
            "output": output,
            "output_present": bool(output and output in have),
            "note": note,
            "checkbox": info[5] if info else None,
        },
        "gate_waiting": waiting,
        "gate_checkbox": BY_ID[waiting][5] if waiting else None,
        "empty_parts": empty,
        "gates": gates,
    }


def text_line(state):
    nxt = state["next"]
    if nxt["id"] == "fertig":
        return "fertig"
    label = f"{nxt['id']} {nxt['name']}"
    if nxt["id"] == "5b":
        label += " (Agent schreibt, Lars sieht durch" + (", " + nxt["note"] if nxt["note"] else "") + ")"
    elif nxt["id"] == "9":
        label += " (Lars merged dev in main)"
    elif nxt["id"] == "10":
        label += " (Entwurf in Buttondown)"
    return label


def main(argv):
    args = argv[1:]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    if len(args) != 1:
        print(__doc__)
        return 1
    folder = pathlib.Path(args[0])
    if not folder.is_dir():
        print(f"kein Ordner: {folder}")
        return 1
    state = infer(folder)
    if as_json:
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0
    print("Dateien:", ", ".join(state["files"]))
    if state["empty_parts"]:
        print("Teile ohne Text:", ", ".join(state["empty_parts"]))
    print("Nächste Stufe:", text_line(state))
    if state["gate_waiting"]:
        print("Offener Prüfpunkt: Stufe", state["gate_waiting"], BY_ID[state["gate_waiting"]][1])
    print("Letzte Prüfpunkte:")
    for line in state["gates"][-3:] or ["  (keine)"]:
        print(" ", line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
