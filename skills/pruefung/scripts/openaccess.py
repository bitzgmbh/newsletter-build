#!/usr/bin/env python3
"""Check whether the scientific publications an edition links to are open access.

Usage: openaccess.py index.qmd [more files]

Finds every DOI in the links of a markdown or qmd file (https://doi.org/...
or a DOI inside a publisher URL), skipping HTML comments and code fences, and
asks OpenAlex for its open access status; Semantic Scholar is the fallback.
No key and no contact address is sent. Prints one line per DOI:

  offen    <doi>  <status>  <free copy, when known>
  zu       <doi>  Hinweis steht      the line already carries the note
  HINWEIS  <doi>  Hinweis fehlt      closed, and no note next to the link
  ?        <doi>  nicht gefunden     look it up by hand

The note is "nicht frei zugänglich" in German and "not open access" in
English, in the same line as the link. Exit 0 when nothing is missing, 2 when
a note is missing or a DOI could not be checked, 1 on usage error.
"""
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

DOI = re.compile(r"10\.\d{4,9}/[^\s<>()\"'\]]+")
URL = re.compile(r"https?://[^\s<>()\"'\]]+")
NOTE = re.compile(r"nicht frei zugänglich|not open access", re.I)
UA = {"User-Agent": "bitz-newsletter-pruefung/1.0 (open access check)"}


def dois(text):
    """(doi, line) for every DOI found in a link, in order, once each."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    seen, out = set(), []
    for line in text.splitlines():
        for u in URL.finditer(line):
            m = DOI.search(urllib.parse.unquote(u.group(0)))
            if not m:
                continue
            d = m.group(0).rstrip(".,;:").lower()
            if d not in seen:
                seen.add(d)
                out.append((d, line))
    return out


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except Exception:
        return None


def status(doi):
    """(is_open, label, free_url) or (None, reason, '')."""
    d = fetch("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/"))
    if d and "open_access" in d:
        oa = d["open_access"]
        return bool(oa.get("is_oa")), str(oa.get("oa_status") or ""), str(oa.get("oa_url") or "")
    d = fetch("https://api.semanticscholar.org/graph/v1/paper/DOI:" + urllib.parse.quote(doi, safe="/")
              + "?fields=isOpenAccess,openAccessPdf")
    if d and "isOpenAccess" in d:
        pdf = d.get("openAccessPdf") or {}
        return bool(d["isOpenAccess"]), str(pdf.get("status") or "").lower(), str(pdf.get("url") or "")
    return None, "nicht gefunden", ""


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    missing = 0
    for path in argv[1:]:
        found = dois(open(path, encoding="utf-8").read())
        if not found:
            print(f"{path}: keine DOI in den Links")
            continue
        for doi, line in found:
            is_open, label, url = status(doi)
            if is_open is None:
                missing += 1
                print(f"?        {doi}  {label}")
            elif is_open:
                print(f"offen    {doi}  {label}  {url}".rstrip())
            elif NOTE.search(line):
                print(f"zu       {doi}  Hinweis steht")
            else:
                missing += 1
                print(f"HINWEIS  {doi}  Hinweis fehlt ({label})")
    return 2 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
