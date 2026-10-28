# pruefung

The skill for stage 6 of the pipeline. It checks an edition and writes a report. It never edits the edition (decision 0016).

## Why I use it

A wrong link or a wrong number must not go out. The skill reads as the Schlussredaktion of a newspaper: every fact, number and date must trace to a source in `recherche.md`, a link or a code chunk, and every link must resolve. Those are hard checks, and a fail blocks the edition. The rest are hints I decide on: the word count per part against the template, the AI tells in German, five reader personas who each say where they stop reading, and three perspectives (Psychologie, Didaktik, Philosophie, decision 0018) that each name what the text misses. The persona of the edition's Hauptleserschaft speaks last. The report lands as `pruefbericht.md` next to the edition.

## What is in here

- `SKILL.md`: the checks, what counts as a fail, and the shape of the report.
- `personas.md`: the five readers of the review stage, as roles.
- `blickwinkel.md`: the three perspectives, as decided in 0018.
- `scripts/links.py`: requests every link in a file and reports the status.

## Install

Link this folder into `~/.claude/skills/pruefung/`. It uses `skills/stimme/scripts/woerter.py` for the word count and the edition folders of the private repository.
