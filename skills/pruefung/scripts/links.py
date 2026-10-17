#!/usr/bin/env python3
"""Check the links of an edition.

Usage: links.py index.qmd [more files]

Extracts every http(s) URL from a markdown or qmd file, skipping HTML
comments and code fences, and requests each one: HEAD first, GET when HEAD
is refused, 10 seconds timeout. Prints one line per URL with the status.
Exit 0 when every link resolves, 2 when any failed, 1 on usage error.
"""
import re
import sys
import urllib.error
import urllib.request

URL = re.compile(r"https?://[^\s<>()\"'\]]+")
UA = {"User-Agent": "zur-einsicht-pruefung/1.0 (link check)"}


def urls(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    seen = []
    for m in URL.finditer(text):
        u = m.group(0).rstrip(".,;:")
        if u not in seen:
            seen.append(u)
    return seen


def status(url):
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers=UA)
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, ""
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue
            return e.code, ""
        except Exception as e:  # timeout, DNS, TLS
            if method == "HEAD":
                continue
            return None, type(e).__name__
    return None, "no response"


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    failed = 0
    for path in argv[1:]:
        text = open(path, encoding="utf-8").read()
        found = urls(text)
        if not found:
            print(f"{path}: keine Links")
            continue
        for u in found:
            code, err = status(u)
            ok = code is not None and 200 <= code < 400
            failed += 0 if ok else 1
            mark = "ok  " if ok else "FAIL"
            print(f"{mark} {code if code is not None else err:>4}  {u}")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
