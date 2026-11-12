"""Turn an approved edition into a Buttondown draft (stage 10).

The app only ever creates drafts (status "draft"). Lars checks the preview in
Buttondown and presses send there. The API key comes from the macOS Keychain,
service "bitz-buttondown", and is read only at the moment of the upload.
"""
import html
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import httpx
import yaml

from .config import Config

API = "https://api.buttondown.com/v1"
KEYCHAIN_SERVICE = "bitz-buttondown"
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)([^)]*)\)")


class VersandError(RuntimeError):
    pass


def api_key() -> str:
    p = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
                       capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        raise VersandError(
            f"Kein Buttondown Schlüssel im Schlüsselbund (Dienst {KEYCHAIN_SERVICE}). Einmal anlegen mit: "
            f"security add-generic-password -s {KEYCHAIN_SERVICE} -a lars -w"
        )
    return p.stdout.strip()


def _lookup(data: dict, dotted: str) -> str:
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return ""
        cur = cur[part]
    return str(cur)


def _split(text: str) -> tuple[dict, str]:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return yaml.safe_load(text[3:end]) or {}, text[end + 4:]
    return {}, text


def _img_to_markdown(m: re.Match) -> str:
    tag = m.group(0)
    src = re.search(r'(?<![\w-])src="([^"]*)"', tag)
    if not src:
        return tag
    alt = re.search(r'(?<![\w-])alt="([^"]*)"', tag, flags=re.S)
    text = html.unescape(alt.group(1)) if alt else ""
    text = re.sub(r"\s+", " ", text).replace("[", "(").replace("]", ")").strip()
    return f"![{text}]({src.group(1)})"


def clean_markdown(body: str, meta: dict, variables: dict) -> str:
    """Markdown for the email from Quarto source or Quarto's gfm output."""
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r"\{\{<\s*meta\s+([\w.-]+)\s*>\}\}", lambda m: _lookup(meta, m.group(1)), body)
    body = re.sub(r"\{\{<\s*var\s+([\w.-]+)\s*>\}\}", lambda m: _lookup(variables, m.group(1)), body)
    # gfm output writes divs as HTML; Quarto source writes fenced divs.
    body = re.sub(r'<div class="nur-web"[^>]*>.*?</div>', "", body, flags=re.S)
    body = re.sub(r"(?ms)^:::+\s*\{\.nur-web[^}]*\}\s*$.*?^:::+\s*$", "", body)
    body = re.sub(r"(?m)^:::+.*$", "", body)
    body = re.sub(r"</?div[^>]*>", "", body)
    # Quarto's gfm output writes a figure with alt text as an HTML <img>; the
    # upload and the email need the markdown form.
    body = re.sub(r"<img\b[^>]*>", _img_to_markdown, body, flags=re.S)
    body = re.sub(r"(?m)^\*Reihe:\s*\*\s*$", "", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip() + "\n"


def has_code(qmd_text: str) -> bool:
    """True when the edition has a chunk Quarto must run (comments do not count)."""
    text = re.sub(r"<!--.*?-->", "", qmd_text, flags=re.S)
    return bool(re.search(r"(?m)^```\{(r|python|ojs)", text))


def drop_title_block(body: str, meta: dict) -> str:
    """Quarto's gfm output starts with the title and the date; the email has its own subject."""
    lines = body.lstrip("\n").splitlines()
    title, date = str(meta.get("title") or ""), str(meta.get("date") or "")
    if lines and title and lines[0].strip() == f"# {title}":
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
        if lines and date and lines[0].strip() == date:
            lines = lines[1:]
    return "\n".join(lines).lstrip("\n")


def render(cfg: Config, folder: Path, qmd_name: str = "index.qmd") -> tuple[dict, str, Path | None]:
    """Return (metadata, markdown body, folder that holds rendered images)."""
    source = (folder / qmd_name).read_text(encoding="utf-8")
    meta, body = _split(source)
    var_file = cfg.repo_path / "_variables.yml"
    variables = yaml.safe_load(var_file.read_text(encoding="utf-8")) if var_file.exists() else {}
    if not has_code(source):
        return meta, clean_markdown(body, meta, variables), folder

    if not cfg.quarto:
        raise VersandError("Die Ausgabe hat Code, aber Quarto wurde nicht gefunden (QUARTO_PATH setzen).")
    tmp = Path(tempfile.mkdtemp(prefix="bitz-versand-"))
    ignore = shutil.ignore_patterns(".git", "_site", ".quarto", ".Rproj.user", "_freeze")
    shutil.copytree(cfg.repo_path, tmp / "repo", ignore=ignore)
    rel = folder.relative_to(cfg.repo_path)
    # wrap:none keeps a paragraph on one line; Buttondown shows the line ends of a
    # wrapped paragraph as breaks in the mail.
    p = subprocess.run([cfg.quarto, "render", str(rel / qmd_name), "--to", "gfm", "-M", "wrap:none"],
                       cwd=tmp / "repo", capture_output=True, text=True)
    out_dir = tmp / "repo" / "_site" / rel
    md = out_dir / (Path(qmd_name).stem + ".md")
    if p.returncode != 0 or not md.exists():
        raise VersandError("Quarto konnte die Ausgabe nicht rendern:\n" + (p.stderr or p.stdout)[-2000:])
    _, rendered = _split(md.read_text(encoding="utf-8"))
    return meta, clean_markdown(drop_title_block(rendered, meta), meta, variables), out_dir


def check_fields(meta: dict) -> list[str]:
    problems = []
    for key, label in (("subtitle", "Betreff (subtitle)"), ("description", "Vorschautext (description)"),
                       ("title", "Titel")):
        value = str(meta.get(key) or "")
        if not value or "TODO" in value:
            problems.append(f"{label} fehlt oder steht noch auf TODO")
    return problems


def local_images(body: str) -> list[str]:
    return [m.group(2) for m in IMG_RE.finditer(body) if not m.group(2).startswith(("http://", "https://"))]


def upload_images(body: str, image_root: Path, key: str) -> str:
    def repl(m):
        src = m.group(2)
        if src.startswith(("http://", "https://")):
            return m.group(0)
        path = (image_root / src).resolve()
        if not path.exists():
            raise VersandError(f"Bild nicht gefunden: {src}")
        with path.open("rb") as fh:
            r = httpx.post(f"{API}/images", headers={"Authorization": f"Token {key}"},
                           files={"image": (path.name, fh)}, timeout=60)
        if r.status_code not in (200, 201):
            raise VersandError(f"Bild {src} nicht hochgeladen: {r.status_code} {r.text[:300]}")
        return f"![{m.group(1)}]({r.json()['image']}{m.group(3)})"
    return IMG_RE.sub(repl, body)


def create_draft(meta: dict, body: str, image_root: Path) -> dict:
    key = api_key()
    body = upload_images(body, image_root, key)
    payload = {
        "subject": str(meta["subtitle"]),
        "description": str(meta.get("description") or ""),
        "body": "<!-- buttondown-editor-mode: plaintext -->\n" + body,
        "status": "draft",
    }
    r = httpx.post(f"{API}/emails", headers={"Authorization": f"Token {key}"}, json=payload, timeout=60)
    if r.status_code not in (200, 201):
        raise VersandError(f"Buttondown hat den Entwurf abgelehnt: {r.status_code} {r.text[:500]}")
    data = r.json()
    return {"id": data.get("id", "?"), "url": f"https://buttondown.com/emails/{data.get('id', '')}"}
