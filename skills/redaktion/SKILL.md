---
name: redaktion
disable-model-invocation: true
description: >-
  Decide the open gate of a bitz edition here in Claude Code, with decision
  boxes, while the Redaktion app runs the stages and keeps the log (decision
  0034). Reads the state and the marked open points from the app, asks Lars
  in German boxes with a recommendation first, sends his verdict to the app,
  waits for the run and goes on to the next gate. Stops before stage 9
  (Freigabe) and 10 (Buttondown), which stay buttons in the app. Use only
  when Lars invokes /redaktion, with or without an edition.
---

# redaktion

The app in `app/` shows the stages, runs the runner and keeps the run log. This skill is where Lars decides: it turns the open points of a gate into decision boxes, sends his verdict to the app, and follows the run to the next gate. It never writes edition text and never starts a run without his answers.

## Setup

- The app's address is `app_url` in `~/.config/bitz-newsletter.json` (default `http://127.0.0.1:8765`). Check it with `curl -s <app_url>/api/ausgaben`. If that fails, the app is not running: tell Lars to start it in its own terminal with `cd <build repo>/app && uv run redaktion`, and stop. Do not start the app from this session; it would end with the session.
- Text to Lars stays English. The boxes are German, because they quote the edition and the verdict lands in German in `pruefpunkte.md`.

## Which edition

- With an argument, use it: a folder name (`2026-11-10-lernen-am-eigenen-projekt`) or the short name (`lernen-am-eigenen-projekt`). The app resolves both.
- Without one, read `GET /api/ausgaben` (sorted by send date) and take the first edition with `gate_waiting`. Say in one line which edition and which gate. If none waits, say what each edition's next stage is and stop.

## One gate

1. `GET /api/ausgabe/<name>` gives `gate_waiting`, `gate_name`, `datei` (the stage's output file), `tab` and `link` (the app tab to read), `punkte` (the marked open points: "?" in outline and text, Fail and Hinweis in the check report, bullets under "Offen"), `unsaved` and, at stage 6, `bericht` (verdict and counts).
2. If `unsaved` lists files, Positron holds unsaved changes. Ask Lars to save (Cmd+S) and wait for his word before going on; the app refuses a run while they are unsaved.
3. Read the output file and the parts of `index.qmd` the points refer to, in the private repository (`private_repo_path` in the config, folder `ausgaben/<name>/`). Read only; this skill commits nothing.
4. Tell Lars in two or three lines what the stage produced, and give the link to the tab. At stage 6 add the counts (bestanden, Hinweis, Fail per check) and the report's verdict.
   - At stage 7, also render the chart for him: copy the edition folder to the scratchpad, render `index.qmd` there with Quarto (the bundled binary `/Applications/RStudio.app/Contents/Resources/app/quarto/bin/quarto` when `quarto` is not on the PATH), and `open` the figure PNG in Preview. Never render inside the repository.
5. Ask the boxes (AskUserQuestion), at most four per call, in German:
   - One box per point that needs a decision from Lars. Group points that are one decision. A point that needs no decision (a note on the repository, a reminder for later) is not a box; list those in one line after the boxes.
   - The question quotes the sentence or finding it is about, short enough to read at a glance.
   - Two to four options, each a concrete answer the runner can carry out. The recommended one comes first, marked "(Empfohlen)", with the reason in its description. Use a preview for sentence variants or a chart layout.
   - No closing "Sonst noch etwas?" box; Lars uses "Other" for free text on any box.
   - When the gate has no marked points, ask one box: "Passt Stufe <n> <Name> so?" with "Ja, weiter" first.
6. Build the verdict from his answers:
   - Every answer accepts the result as it is: verdict `ja`.
   - At least one answer asks for a change: one final box, "Einarbeiten und weiter" (art `ja, mit Änderungen`) or "Einarbeiten, dann noch einmal ansehen" (art `geändert`). Recommend "weiter" for small fixes and "ansehen" when a whole part changes.
   - The text names, per point, where it is (file and part) and what to do, in German and in Lars's words where he wrote some. Free text from "Other" goes in as he wrote it.
   - A wish to send the edition back a stage is `art: blockiert` with `zurueck` (5b, 5a or 4); ask it only when an answer says so.
7. `POST /api/ausgabe/<name>/urteil` with JSON `{"art": ..., "text": ...}`. Say in one line that run #<id> started and give its link.

## Waiting and going on

- Wait for the run without polling in the foreground: one background command that loops on `GET /api/lauf/<id>` every 20 seconds until `status` is no longer `läuft`, then prints status, cost and `result`.
- While it runs, say nothing more. Lars can watch the run in the app.
- When it ends:
  - `fehler` or `abgebrochen`: give the last lines of the result and the link, and stop.
  - `fertig`: sum up the report in two or three lines (what changed, what is still open), then read the state again. A new open gate: go back to "One gate". Next stage 9 or 10: give the app link (`<app_url>/ausgabe/<name>/freigabe` or `/versand`) and stop. No gate open and an agent stage next (for example 5b after a yes at 5a): the runner already ran it; read the state again.
- Stop whenever Lars says stop.

## What this skill does not do

- Freigabe (stage 9) or the Buttondown draft (stage 10). In the app those are buttons; from the terminal, stage 10 is the [versand](../versand/) skill (decision 0037).
- Write or change edition text, `pruefpunkte.md` or any file in the repositories. The runner does that in the run.
- Start the app, push, or edit the GitHub issue.
- Send anything to Element (0034).
