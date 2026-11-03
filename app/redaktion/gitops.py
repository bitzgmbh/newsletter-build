"""The few git commands the app runs itself.

Commits name their paths, so anything Lars has staged for his own commit stays
staged and out of the app's commit. The app never checks out another branch:
Freigabe fast-forwards main to dev on the remote and in the local ref.
"""
import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


def git(repo: Path, *args: str, check: bool = True) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise GitError(f"git {' '.join(args)}: {p.stderr.strip() or p.stdout.strip()}")
    return p.stdout.strip()


def current_branch(repo: Path) -> str:
    return git(repo, "rev-parse", "--abbrev-ref", "HEAD")


def commit_paths(repo: Path, paths: list[str], message: str) -> str:
    """Commit exactly these paths (new files are added first)."""
    git(repo, "add", "--", *paths)
    git(repo, "commit", "-q", "-m", message, "--only", "--", *paths)
    return git(repo, "rev-parse", "--short", "HEAD")


def push(repo: Path, refspec: str, dry_run: bool) -> str:
    if dry_run:
        return f"Trockenlauf: git push origin {refspec} ausgelassen"
    git(repo, "push", "-q", "origin", refspec)
    return f"git push origin {refspec}"


def freigabe_preview(repo: Path, folder: str) -> dict:
    """What a fast-forward of main to dev would bring along."""
    git(repo, "fetch", "-q", "origin", check=False)
    base = "origin/main" if git(repo, "rev-parse", "--verify", "-q", "origin/main", check=False) else "main"
    files = [f for f in git(repo, "diff", "--name-only", f"{base}...dev").splitlines() if f]
    mine = [f for f in files if f.startswith(folder + "/")]
    others = [f for f in files if not f.startswith(folder + "/")]
    ff = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", base, "dev"]).returncode == 0
    diff = git(repo, "diff", f"{base}...dev", "--", folder)
    return {"base": base, "mine": mine, "others": others, "fast_forward": ff, "diff": diff}
