# Redaktion

A small local app in front of the bitz pipeline (decision 0028). It shows every raw draft and edition by stage, starts the runner for the next stage, takes my verdict at each gate, does the Freigabe and creates the Buttondown draft (decision 0029). It runs on my Mac only, for me only, and the screens are in German.

## What it does and does not do

- The stage of an edition always comes from `skills/runner/scripts/stand.py`, the same script the runner reads.
- Every agent stage goes through the runner. The app starts it headless (`claude -p`, `stream-json`) with the verdict I clicked and shows the run live, with the cost at the end. The runner commits, ticks the issue and sends the Element notice.
- Three buttons are mine alone and the app does them itself: "Ausgabe anlegen" from a draft in `_entwuerfe/`, "Freigeben" (stage 9) and "Entwurf in Buttondown anlegen" (stage 10).
- The app itself never writes the text of an edition; the skill stimme does that in a run (0032), and my own edits at gate 5b are committed as mine before the next run. It never sends an email, and never checks out another branch. Freigabe only fast-forwards `main` to `dev`.
- I can also decide the gates in Claude Code with `/redaktion` (skills/redaktion, decision 0034). It uses the JSON endpoints under `/api/` and starts runs the same way the buttons do. When a run ends, the app shows a macOS notification; there is no Element ping any more.
- Run history lives in `~/.local/share/bitz-redaktion/runs.db`, outside git. The repository stays the record.

## Start

```sh
cd app
uv run redaktion
```

Then open <http://127.0.0.1:8765>. It reads `~/.config/bitz-newsletter.json` (`private_repo`, `private_repo_path`, and optionally `app_url`).

Once, for the Buttondown step, put the API key into the Keychain:

```sh
security add-generic-password -s bitz-buttondown -a lars -w
```

Quarto renders editions with code (the chart from stage 7). The app looks for it in `QUARTO_PATH`, then in the RStudio bundle.

## Test run

Point the app at a throwaway clone and switch off everything that leaves the Mac:

```sh
REDAKTION_REPO_PATH=/path/to/copy REDAKTION_DRY_RUN=1 REDAKTION_DATA=/tmp/redaktion uv run redaktion
```

`REDAKTION_CLAUDE` replaces the `claude` binary (for a fake that prints `stream-json`), `REDAKTION_PORT` the port.

## Tests

```sh
uv run python -m unittest discover tests
python3 -m unittest discover ../skills/runner/tests
```

## Files

- `redaktion/main.py`: routes and the Freigabe and Versand steps.
- `redaktion/editions.py`: editions, drafts, the board, "Ausgabe anlegen".
- `redaktion/runs.py`: headless runs of the runner and their log.
- `redaktion/buttondown.py`: `index.qmd` to email Markdown, image upload, the draft.
- `redaktion/gitops.py`: the few git commands, commits by path only.
- `redaktion/templates/`: the pages (`.j2`, because the repository ignores `*.html`).
