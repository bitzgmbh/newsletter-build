---
name: offenlegung
description: >-
  Writes the block "So ist diese Ausgabe entstanden" of an edition from the
  traces the work left: the commits of the edition folder, their trailers,
  the prompts archive and the re_gent sessions. Never from memory. Use when
  an edition is ready for stage 9, when Lars asks for the Offenlegung of an
  edition, or when the runner reaches that step (decision 0017).
---

# offenlegung

Principle 7 of the map: AI use is declared from the traces the work leaves. For a pull request the [disclosure-summary](../disclosure-summary/) skill counts commits by trailer. For an edition this skill does the same per stage: which stage an agent did, which Lars, with which model. A block typed by hand would come from memory and drift from the record, so the block only ever comes from `offenlegung.R`.

## Run

```sh
Rscript skills/offenlegung/offenlegung.R <edition folder>
```

The script reads the commits that touched the folder (`git log -- <folder>`), their `Assisted-by:`, `Human-authored:` and `Regent-Session:` trailers through git's own trailer parser, the `Prompts:` ids in the messages, and the files each stage left behind (rohentwurf.md, recherche.md, gliederung.md, index.qmd, pruefung-stimme.md, pruefbericht.md with its Urteil, grafiken.md, verbreitung.md). It prints a bullet list of about 60 words. An edition without a single `Assisted-by:` commit gets "Diese Ausgabe ist ganz von Hand entstanden, ohne Agent."

Show the block to Lars. Then, after his yes:

```sh
Rscript skills/offenlegung/offenlegung.R <edition folder> --schreiben
```

This writes the block into `index.qmd` under the heading "So ist diese Ausgabe entstanden", between the markers `<!-- offenlegung:start -->` and `<!-- offenlegung:end -->`, so a later run replaces it. The template comment stays. Commit `index.qmd` on dev in the private repository with the restore/add dance around `rohentwurf.md` (`git restore --staged` before, `git add` after), trailer `Assisted-by: Claude <model-id>`, and push.

Run it last, after the last agent stage and before stage 9, because every later commit changes the traces. If a stage runs again after the block was written, run the script again.

## What this skill never does

- Write or edit the block by hand, or fill a gap the traces do not show.
- Guess a stage from the conversation. A stage without a commit or a file is not in the block.
- Change anything in `index.qmd` outside the two markers.
