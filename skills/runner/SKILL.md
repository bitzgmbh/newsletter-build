---
name: runner
disable-model-invocation: true
description: >-
  Drives one edition of bitz through the pipeline, one stage per
  invocation, with a gate after each agent stage (decision 0014). It infers
  the current stage from the edition folder, runs that stage's skill, commits
  the output on dev in the private repository, pings Lars in Element with a
  link, and stops until his yes. Use when Lars says "nächste Stufe", "weiter
  mit der Ausgabe", or invokes /runner <edition folder> [verdict]. The app
  in app/ calls it headless with the verdict Lars clicked.
---

# runner

The runner is the shared step around the stage skills: it calls the skill for the next stage, records the gate, and asks Lars for his yes in Element. One invocation moves an edition by one stage and then stops. The gates and the rule for dropping one are in `pipeline/concept.md` (Breite); the stages are on the map in `pipeline/map.qmd`.

## Config

Read `~/.config/bitz-newsletter.json`: `element_room` (the Matrix room for the pings), `private_repo` (owner/name), `private_repo_path` (the local clone), and `app_url` (optional, the address of the app, for example `http://127.0.0.1:8765`). If the file or a required key is missing, say which one and stop. Nothing from that file goes into a commit or a committed file.

## Input

An edition folder in the private repository, `ausgaben/<JJJJ-MM-TT-kurzname>/`. If none is named, list the folders and ask.

Optionally a verdict after the folder, as the app passes it: `ja`, `geändert: "<sätze>"` or `blockiert, zurück zu <Stufe>`. A verdict given this way is Lars's answer to the open gate; do not look for one in the chat or the room. Optionally also `--quelle "<text>"` for stage 7: the data source Lars named, passed to grafiken.

## State

Run `scripts/stand.py --json <edition folder>` first. It infers the stage from the files present and from `pruefpunkte.md`, names the gate that waits for Lars (`gate_waiting`) and the issue checkbox labels, and lists the gate lines. `STAGES` in that script is the one place for stage names and checkbox labels. The order:

| Stage | Produces | Skill | Then |
|---|---|---|---|
| 4 Recherche | `recherche.md` | recherche | gate |
| 5a Gliederung | `gliederung.md` | stimme, mode gliederung | gate |
| 5b Text | parts of `index.qmd` with text | Lars writes; the runner waits | no gate, runs 5c when the parts have text |
| 5c Prüfung stimme | `pruefung-stimme.md` | stimme, mode pruefung | gate |
| 6 Prüfungen | `pruefbericht.md` | pruefung | gate; an Urteil "blockiert" sends the edition back to 5b |
| 7 Grafiken | `grafiken.md`, and the chart block in `index.qmd` | skill grafiken | gate |
| 8 Übersetzung | `index-en.qmd` | uebersetzung | gate |
| Offenlegung (0017) | the block in `index.qmd` | offenlegung: run the script after the last agent stage, show the block in the ping for stage 9, write it with `--schreiben` after the yes | part of the stage 9 ping |
| 9 Freigabe | merge of dev into main | Lars, with the button in the app | the app writes the line `9 Freigabe: ja` |
| 10 Versand | a draft in Buttondown | Lars, with the button in the app | the app writes the line `10 Versand: Entwurf <id>` |
| 11 Verbreitung | `verbreitung.md`, one post per channel | skill verbreitung | gate: the ping carries the first line of each post |

A stage whose skill is not built stops with "Skill fehlt: <name>" and pings Lars with that line, so the pipeline runs end to end with its gaps named. For 5b, check the parts with `skills/stimme/scripts/woerter.py <folder>/index.qmd`; when every part except "Was ihr letztes Mal gesagt habt" has words, 5b is done.

## One invocation

1. Read the config and run `stand.py`. Say in one line which stage comes next.
2. If `gate_waiting` names a stage, find the verdict: the verdict argument if there is one, else Lars's answer in the chat, or a message from him in the room after the runner's last ping (`matrix_get_messages`, newest first). "ja", "ok" or "weiter" is the yes. Anything else is feedback: append it to `pruefpunkte.md` as "geändert: <his sentences>", apply it to the stage's output only if the feedback asks for that, and stop with a ping. Without a verdict, stop and say the gate is open.
3. Append the gate line to `pruefpunkte.md` (format below).
4. Run the stage's skill by following its SKILL.md. Never write or change the text of the edition.
5. Commit in the private repository on dev. Stage only the output files of this stage and `pruefpunkte.md`, by name. `rohentwurf.md` may be staged by Lars for his own commit: run `git restore --staged <folder>/rohentwurf.md` before `git add`, and `git add <folder>/rohentwurf.md` again after the commit, so his staging survives. Never `git add -A`. Trailer: `Assisted-by: Claude <model-id>`. Push dev.
6. If the edition has an issue in the private repository, tick the checkbox of the gate that got its yes (`gate_checkbox` from `stand.py`, for example "5 Gliederung vom Agenten") in its body with `gh issue edit --body-file`, replacing "- [ ] <label>" with "- [x] <label>". If there is no issue, say so once and go on.
7. Ping, then stop.

## The ping

One Matrix message to `element_room`, in German:

```
bitz, <Titel der Ausgabe>: Stufe <n> <Name> fertig, dein Ja?
<two or three lines on what the stage produced: counts, Urteil, open "?" points>
https://github.com/<private_repo>/blob/dev/<path to the output file>
Antworte hier mit ja, oder mit ein bis zwei Sätzen, was ich ändern soll.
<app_url>/ausgabe/<ordnername>
```

When `app_url` is set, the last line links to the edition page in the app, where Lars usually answers. Without it, leave the line out.

## pruefpunkte.md

One line per gate, appended, never rewritten:

```
- <JJJJ-MM-TT HH:MM> Stufe <n> <Name>: <ja | offen | geändert: "<seine Sätze>" | blockiert, zurück zu <Stufe>>
```

This file is the record the autonomy rule reads (concept.md, Breite): a gate may run without a yes once three editions in a row show "ja" at that gate without a change. It is committed with the next stage's output.

## What the runner never does

- Write, complete or change the text of an edition.
- Skip a gate, or treat silence as a yes.
- Merge into main or create anything in Buttondown. Stages 9 and 10 are Lars's buttons in the app.
- Commit outside the edition folder, or put the config values into a file in git.
