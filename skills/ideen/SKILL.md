---
name: ideen
disable-model-invocation: true
description: >-
  The writing workshop for new bitz ideas (stages 1 and 2 of the pipeline,
  decision 0038). Files every new note from the Element room "newsletter"
  (text, voice, photo) as one idea in _ideen/ of the private repository,
  shows the backlog, then takes one idea at a time and grills Lars in
  German in up to three rounds until the idea is parked, dropped, or
  written up as a Rohentwurf in _entwuerfe/, where "Ausgabe anlegen" in the
  app takes over. Use only when Lars invokes /ideen, optionally with an
  idea file or "alle neuen".
---

# ideen

The skill works from one role: Ressortleitung, the editor who decides what becomes a story. The question behind every round is: which one claim, for whom, and why now. Lars's ideas stay his (concept.md, Selbstständigkeit); the skill files them, asks, and writes down his answers. It never writes edition text.

## Files to read first

- `~/.config/bitz-newsletter.json`: `private_repo_path`, `ideas_room_id`, and `vault_path` if set (else `~/Documents/gitrepos/cb-laz/arti-vault`).
- `pipeline/concept.md`, sections "Für wen" and "Breite": the five groups of readers and the roles.
- `pipeline/template.md`: the parts of an edition, so the questions aim at them.
- `skills/stimme/regeln.md`: the German rules. They apply to every line the skill writes into a file.
- `_ideen/*.md` in the private repository: the current backlog.

## Mechanics

Everything that touches files or archive.db goes through `scripts/ideen.py` (standard library only, tests in `tests/`). Run it from this repository:

```sh
python3 skills/ideen/scripts/ideen.py eingang            # new rows of the room into _ideen/
python3 skills/ideen/scripts/ideen.py liste              # the backlog by status
python3 skills/ideen/scripts/ideen.py status DATEI besprochen --text "..."
python3 skills/ideen/scripts/ideen.py rohentwurf DATEI --kurzname NAME --titel TITEL < stichpunkte.md
python3 skills/ideen/scripts/ideen.py notiz --titel T --quelle Q < text.md
```

The script never commits. The skill commits by path after each step, on dev of the private repository, with the authorship trailers (`Assisted-by:` and `Human-authored: true` for the mixed work of a workshop).

## Steps

### 1. Eingang

Run `eingang` (first with `--dry-run` to show what is waiting). Every unprocessed row of the ideas room becomes one file in `_ideen/` with status `neu`, the source id as `quelle`, the form (geschrieben, gesprochen, foto) and the text verbatim; the "Newsletter:" prefix is dropped. Voice messages are transcribed by `~/bin/voice_note_insert.py --in-place` first (language auto; pass `--language de` when Lars says the note is German). Photos are read with the Read tool and described in one sentence under the caption; the file keeps the media path, the image never enters the repository. Rows are marked processed only after their file exists.

Commit: `feat(ideen): N neue Ideen aus dem Raum newsletter`. Report one line per idea.

### 2. Auswahl

Run `liste` and show it as a table: status, date, form, title, file. Ideas with status `neu` first, then `besprochen`. Ask which idea to work on, or take the one Lars named with the command. "alle neuen" means every `neu` idea in turn, one workshop each.

### 3. Werkstatt

Up to three rounds per idea, in German. A round is two to four questions, each with a suggested answer so that "ja" accepts it. Format, without emojis:

```
**F1 Behauptung.** Welche eine Aussage soll die Ausgabe machen? ...
Vorschlag: ...

**F2 Leser:innen.** ...
Vorschlag: ...
```

Round one: the one claim in one sentence; the Hauptleserschaft among Behörde, Hochschule, Privatwirtschaft, NGO, Selbstständig; what those readers do in Excel or by hand today that the idea touches.

Round two: the Zur Einsicht example, an own mistake or lesson from Lars's work or teaching; the Probier es selbst step (R in the browser or an AI prompt, the other one than in the previous edition; check `ausgaben/` for which it was).

Round three: the Rubrik or series it belongs to; why now; what the Recherche must check (claims, numbers, names); the one question for readers.

Facts are the skill's job, never Lars's: earlier editions in `ausgaben/`, his wiki and project pages in the vault, the archive row behind the idea. Look them up before asking. Stop early when Lars says "parken" or "verwerfen".

### 4. Urteil

One of three per idea, written with the script:

- geparkt: `status DATEI besprochen --text "<the answers so far in one or two sentences>"`.
- verworfen: `status DATEI verworfen --text "<the reason in Lars's words>"`. The file stays.
- gewählt: `rohentwurf DATEI --kurzname <name> --titel "<Betreff oder Arbeitstitel>"` with the Rohentwurf on stdin: a bullet list in Lars's own words from his answers, ordered by the parts of the template (Behauptung, Zur Einsicht, Probier es selbst, Frage an die Leser:innen, Hinweise für die Recherche). Never prose; he writes the paragraphs himself (0015). The script marks the idea `gewählt` and links the draft.

Commit by path after each idea: `feat(ideen): <kurzname> <besprochen|verworfen|gewählt>`.

Then one line in today's journal of the vault (`journals/YYYY_MM_DD.md`, create the file if it is missing, append at the end):

```
- bitz idea discussed: "<titel>", <geparkt|verworfen|gewählt> (_ideen/<file>) #[[para/projects/bitz-newsletter]]
```

### 5. Bericht

End with one line per idea worked on, the counts by status, and for each `gewählt` idea the pointer: the draft is in `_entwuerfe/`, "Ausgabe anlegen" in the app or `/runner` takes it from there.

## Rules

- German in every file and in the workshop (decision 0038); Swiss spelling, the Leser:innen form, no dashes, no emojis (`skills/stimme/regeln.md`).
- Never writes edition text, never sends anything, never copies media into the repository, never touches another branch, never edits `ausgaben/`.
- Ideas are Lars's words. The skill shortens nothing in `_ideen/`; it adds the Verlauf lines and the status.
- Personal data in a note (names of other people, addresses) is pointed out at the first round and stays out of the Rohentwurf unless Lars says otherwise.
- The app shows the backlog read-only under Ideen; it runs nothing (0037).
