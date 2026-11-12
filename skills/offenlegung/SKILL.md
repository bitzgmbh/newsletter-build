---
name: offenlegung
disable-model-invocation: true
description: >-
  Writes the block "Offengelegt" of an edition from the
  traces the work left: the commits of the edition folder, their trailers,
  and the sentences Lars confirmed in offenlegung.md. Never from memory. Use when
  an edition is ready for stage 9, when Lars asks for the Offenlegung of an
  edition, or when the runner reaches that step (decisions 0017 and 0040).
---

# offenlegung

Principle 7 of the map: AI use is declared from the traces the work leaves. For a pull request the [disclosure-summary](../disclosure-summary/) skill counts commits by trailer. For an edition this skill writes a block a reader can follow (decision 0040): who wrote the text, what Claude Code did, one line per verb, which model, who decided, and a link to [disclosure.md](../../disclosure.md). The block only ever comes from `offenlegung.R`.

## Run

```sh
Rscript skills/offenlegung/offenlegung.R <edition folder>
```

The script reads the commits that touched the folder (`git log -- <folder>`), their `Assisted-by:` and `Human-authored:` trailers through git's own trailer parser, the 5b gate lines in `pruefpunkte.md`, and the files each stage left behind (recherche.md, gliederung.md, index.qmd, pruefung-stimme.md, pruefbericht.md, grafiken.md, index-en.qmd, verbreitung.md). A stage file whose text starts with "Entfällt" is not a run. On stderr it tells Lars what the traces hold (commits, archived prompts, re_gent sessions); that line is not part of the block. An edition without a single `Assisted-by:` commit gets "Diese Ausgabe ist ganz von Hand entstanden, ohne KI."

## The confirmed sentences

Some things no trace gives on its own: what Claude Code proposed in the chat, what a check found, who read the draft before the send. They go into `offenlegung.md` next to the edition, one line per key:

```
Text: Den Text habe ich am 9. November selbst geschrieben.
Vorgeschlagen: fünf Änderungen zur Lesbarkeit. Jeden Vorschlag habe ich einzeln angenommen oder gestrichen.
Rückmeldung: Zwei Personen haben vor dem Versand Rückmeldung zum Entwurf gegeben.
```

Keys: Text, Recherchiert, Gegliedert, Geprüft, Vorgeschlagen, Gebaut, Übersetzt, Verbreitet, Rückmeldung. A sentence replaces the default of its key or adds a line the traces do not have.

Draft the sentences from `pruefpunkte.md` and the commit messages of the edition, nothing else. Show them to Lars with the block the script prints. Only sentences he confirmed go into the file. Names of people who gave feedback appear only with their yes.

## Write

After his yes:

```sh
Rscript skills/offenlegung/offenlegung.R <edition folder> --schreiben
Rscript skills/offenlegung/offenlegung.R <edition folder> --en --schreiben
```

The first writes the block into `index.qmd` under the heading "Offengelegt", between the markers `<!-- offenlegung:start -->` and `<!-- offenlegung:end -->`, so a later run replaces it. The second writes the English block into `index-en.qmd` (decision 0030), from the same traces and from `offenlegung-en.md`, which holds the same sentences in English under the keys Text, Researched, Outlined, Checked, Proposed, Built, Translated, Shared, Feedback. Commit the edition folder on dev in the private repository, trailers `Assisted-by: Claude <model-id>` and `Human-authored: true` (Lars confirmed the sentences).

Run it last, after the last agent stage and before stage 9, because every later commit changes the traces. If a stage runs again after the block was written, run the script again.

## What this skill never does

- Write or edit the block in `index.qmd` or `index-en.qmd` by hand.
- Put a sentence into `offenlegung.md` that Lars has not confirmed, or one that `pruefpunkte.md` and the commits do not carry.
- Guess a stage from the conversation. A stage without a commit or a file is not in the block unless a confirmed sentence names it.
- Change anything outside the two markers.
