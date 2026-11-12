"""The open points ("?") in a stage result, and Lars's answers to them.

The stage skills mark an open point with a "?" that stands on its own, at the
end of a line or at its start ("? Betreff: ..."). A question mark glued to a
word ("Was mache ich hier?") is part of a quote and not an open point.

Lars marks his own open points with "TODO" when he reads a text in Positron,
also inside a heading. A TODO inside a template comment is not his and is
skipped.
"""
import re

STANDALONE_Q = re.compile(r"(^|\s)\?(\s|$)")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
BOLD_LABEL = re.compile(r"^\*\*([^*]+?):?\*\*")
LIST_MARK = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
TODO = re.compile(r"\bTODO\b")


def open_points(markdown: str) -> list[dict]:
    """Return one entry per line that carries a standalone "?"."""
    points, section, in_comment = [], "", False
    for line in markdown.splitlines():
        was_in_comment = in_comment or "<!--" in line
        if "<!--" in line and "-->" not in line.split("<!--", 1)[1]:
            in_comment = True
        elif in_comment and "-->" in line:
            in_comment = False
        h = HEADING.match(line)
        if h and TODO.search(line):
            title, _, note = h.group(2).partition("TODO")
            section = title.strip(" (")
            points.append({"n": len(points) + 1, "section": section,
                           "text": "TODO" + note.rstrip(") ").rstrip()})
            continue
        if h:
            # the document title (#) is not a part of the edition
            section = "Allgemein" if len(h.group(1)) == 1 else h.group(2).strip()
            continue
        if TODO.search(line) and not was_in_comment:
            text = line.strip()
            idx = text.find("TODO")
            before = text[:idx].strip().strip(' ".:')
            text = text[idx:].rstrip('"')
            if before and len(before) > 60:
                text += " (nach: ..." + before[-60:] + ")"
            elif before:
                text += f" (nach: {before})"
            points.append({"n": len(points) + 1, "section": section, "text": text})
            continue
        if section.lower().startswith("offen") and LIST_MARK.match(line):
            text = LIST_MARK.sub("", line).strip()
            points.append({"n": len(points) + 1, "section": section, "text": text})
            continue
        if not STANDALONE_Q.search(line):
            continue
        text = LIST_MARK.sub("", line).strip()
        label = BOLD_LABEL.match(text)
        where = section
        if label:
            where = f"{section}, {label.group(1)}" if section else label.group(1)
        clean = re.sub(r"\*\*|<!--|-->", "", text)
        clean = re.sub(r"(^|\s)\?(\s|$)", r"\1\2", clean).strip()
        points.append({"n": len(points) + 1, "section": where, "text": clean})
    return points


def feedback(filename: str, points: list[dict], answers: dict[int, str], general: str) -> str:
    """One line for pruefpunkte.md and the runner: the answers, by point."""
    parts = []
    for p in points:
        a = answers.get(p["n"], "").strip()
        if a:
            short = p["text"] if len(p["text"]) <= 90 else p["text"][:87] + "..."
            parts.append(f'Punkt {p["n"]} ({p["section"] or "ohne Teil"}: {short}): {a}')
    if general.strip():
        parts.append("Allgemein: " + general.strip())
    if not parts:
        return ""
    text = f"In {filename} einarbeiten. " + " | ".join(parts)
    return " ".join(text.replace('"', "'").split())
