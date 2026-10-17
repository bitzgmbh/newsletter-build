#!/usr/bin/env python3
"""Print where an edition stands in the pipeline.

Usage: stand.py <edition folder>

Infers the next stage from the files in the folder and from pruefpunkte.md,
lists the files present, and prints the last three gate lines.
"""
import pathlib
import re
import sys

PARTS_OPTIONAL = {"Was ihr letztes Mal gesagt habt"}


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


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 1
    folder = pathlib.Path(argv[1])
    if not folder.is_dir():
        print(f"kein Ordner: {folder}")
        return 1
    have = {p.name for p in folder.iterdir() if p.is_file()}
    print("Dateien:", ", ".join(sorted(have)))

    gates = []
    pp = folder / "pruefpunkte.md"
    if pp.exists():
        gates = [l for l in pp.read_text(encoding="utf-8").splitlines() if l.startswith("- ")]
    last = gates[-1] if gates else ""

    if "recherche.md" not in have:
        stage = "4 Recherche"
    elif "gliederung.md" not in have:
        stage = "5a Gliederung"
    elif "pruefung-stimme.md" not in have:
        counts = parts_with_text(folder / "index.qmd") if "index.qmd" in have else {}
        empty = [n for n, c in counts.items() if c == 0 and n not in PARTS_OPTIONAL]
        stage = "5b Text (Lars schreibt)" if (not counts or empty) else "5c Prüfung stimme"
        if empty:
            print("Teile ohne Text:", ", ".join(empty))
    elif "pruefbericht.md" not in have or "zurück zu 5b" in last:
        stage = "6 Prüfungen" if "pruefbericht.md" not in have else "5b Text (nach blockiertem Urteil)"
    elif "7 Grafiken: ja" not in " ".join(gates):
        stage = "7 Grafiken"
    elif "8 Übersetzung: ja" not in " ".join(gates):
        stage = "8 Übersetzung"
    else:
        stage = "9 Freigabe (Lars merged dev in main), dann 10 Versand, 11 Verbreitung"
    print("Nächste Stufe:", stage)

    print("Letzte Prüfpunkte:")
    for line in gates[-3:] or ["  (keine)"]:
        print(" ", line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
