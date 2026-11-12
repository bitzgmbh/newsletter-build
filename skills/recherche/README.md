# recherche

The skill for stage 4 of the pipeline. It reads my rough draft and writes `recherche.md` next to the edition: a source for every claim, my own material on the topic, outside context, and earlier editions to point to.

## Why I use it

Stage 6 blocks an edition when a number in the text has no source (decision 0016). Finding those sources before I write saves a round back to 5b. The research also reminds me of what I already have: wiki pages, course material, data packages and notes from my vault. Every item carries a link, and anything the skill could not confirm carries a "?", so I see what is solid before the outline.

## What is in here

- `SKILL.md`: the four parts, the steps, the output and what the skill never does.

## Install

Link this folder into `~/.claude/skills/recherche/`, or let the runner read it by path. It needs the stimme skill's `regeln.md` and, for my own material, the path of the arti-vault graph (`vault_path` in `~/.config/bitz-newsletter.json`, with a default).
