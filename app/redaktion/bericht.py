"""A short view of pruefbericht.md (stage 6) for the edition page.

The report of the pruefung skill has "## Hart" with one "###" group per check
(Fakten, Links, Zahlen) whose bullets start with "Bestanden", "Bestanden, mit
Hinweis" or "Fail", then "## Hinweise" with groups of plain bullets, and
"## Urteil". The view counts the hard results per group, lists only what needs
Lars (Fail first, then "mit Hinweis"), and keeps the hints folded.
"""
import re

STATUS = re.compile(r"^(Fail|Bestanden, mit Hinweis|Bestanden)[.:,]?\s*(.*)$", re.S)


def parse(markdown: str) -> dict:
    rep = _parse(markdown)
    rep["punkte"] = points_of_report(rep)
    return rep


def _parse(markdown: str) -> dict:
    part, group, groups, urteil = "", None, [], []
    for line in markdown.splitlines():
        if line.startswith("## "):
            part = line[3:].strip()
            group = None
            continue
        if line.startswith("### "):
            group = {"part": part, "name": line[4:].strip(), "eintraege": [], "other": []}
            groups.append(group)
            continue
        if part == "Urteil":
            if line.strip():
                urteil.append(line.strip())
            continue
        if group is None:
            continue
        if line.startswith("- "):
            text = line[2:].strip()
            m = STATUS.match(text)
            if m and part == "Hart":
                status = {"Fail": "fail", "Bestanden": "ok"}.get(m.group(1), "hinweis")
                group["eintraege"].append({"status": status, "text": m.group(2).strip()})
            else:
                group["eintraege"].append({"status": "info", "text": text})
        else:
            group["other"].append(line)
    for g in groups:
        g["counts"] = {s: sum(1 for i in g["eintraege"] if i["status"] == s) for s in ("ok", "hinweis", "fail", "info")}
        g["body"] = "\n".join(g["other"]).strip()
    text = " ".join(urteil)
    hart = [g for g in groups if g["part"] == "Hart"]
    return {
        "urteil": text,
        "blockiert": text.lower().startswith("blockiert"),
        "hart": hart,
        "fails": sum(g["counts"]["fail"] for g in hart),
        "hinweise": [g for g in groups if g["part"] != "Hart"],
    }


def open_points(markdown: str) -> list[dict]:
    """What Lars decides on: every Fail (muss), then every 'mit Hinweis' (kann)."""
    return points_of_report(parse(markdown))


def points_of_report(rep: dict) -> list[dict]:
    points = []
    for status, art in (("fail", "muss"), ("hinweis", "kann")):
        for g in rep["hart"]:
            for item in g["eintraege"]:
                # a point that only refers to another group ("siehe Fakten") is not asked twice
                if item["status"] == status and not re.search(r"siehe (Fakten|Links|Zahlen)", item["text"]):
                    points.append({"n": len(points) + 1, "section": g["name"], "text": item["text"], "art": art})
    return points
