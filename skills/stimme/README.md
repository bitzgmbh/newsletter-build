# stimme

The skill for stage 5 of the pipeline. It outlines an edition from my rough draft and reviews the text I wrote. It never writes the text itself (decision 0015).

## Why I use it

The voice of the newsletter stays mine, so the agent's job around the text is to order, cut and check. In the mode "gliederung" it turns my rough draft and the research into bullets along the edition template, and I write the paragraphs from them. In the mode "pruefung" it reads what I wrote against the German plain rules in `regeln.md`, the template, the length and my voice in `stimme.md`, and proposes changes one unit at a time through the diff-review skill. I decide per unit. What it changed and what I kept goes into a record next to the edition, and from my verdicts it proposes up to three observations for `stimme.md`, so it learns my voice one edition at a time.

## What is in here

- `SKILL.md`: the two modes and their rules.
- `regeln.md`: the plain rules for German, adapted from the plain-writing skill I use for English.
- `stimme.md`: my voice as observed, growing with each edition. Only I add to it.
- `scripts/woerter.py`: counts the words of an edition per part.

## Install

Link this folder into `~/.claude/skills/stimme/`. It needs the diff-review skill for the review page, and the edition folders of the private repository.
