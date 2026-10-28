#!/usr/bin/env python3
"""Count the words of an edition per part.

Usage: woerter.py index.qmd [--budget template.md]

Skips the YAML front matter, HTML comments, code fences and Quarto shortcodes.
Prints one line per level-two heading with its word count, then the total.
With --budget, reads the word budget per part from pipeline/template.md and
prints the difference.
"""
import re
import sys


def parts(text):
    # front matter
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"\{\{<.*?>\}\}", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"(?m)^\*Reihe:.*$", "", text)
    result = []
    name = "Einstieg"
    buf = []
    for line in text.splitlines():
        if line.startswith("## "):
            result.append((name, buf))
            name, buf = line[3:].strip(), []
        elif line.startswith("#"):
            continue
        else:
            buf.append(line)
    result.append((name, buf))
    return [(n, len(" ".join(b).split())) for n, b in result]


def budgets(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\|\s*([^|]+?)\s*\|[^|]*\|\s*(\d+)\s*\|", line)
        if m and not m.group(1).startswith("**"):
            out[m.group(1)] = int(m.group(2))
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    text = open(argv[1], encoding="utf-8").read()
    counts = parts(text)
    total = sum(n for _, n in counts)
    for name, n in counts:
        print(f"{n:5d}  {name}")
    print(f"{total:5d}  Total (Budget 1000)")
    return 0 if total <= 1000 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
