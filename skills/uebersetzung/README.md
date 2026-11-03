# uebersetzung

The skill for stage 8 of the pipeline. It turns the approved German edition into `index-en.qmd`, which the app sends to Buttondown as a second draft (decisions 0029 and 0030).

## Why I use it

Part of my network does not read German. A full English version as its own email lets them read every edition while the German email stays short. The skill keeps my parts, my chart and my links as they are, writes in the plain English I use elsewhere, and adds nothing. Who gets the English email is still open.

## What is in here

- `SKILL.md`: the rules for the translation, the output and what the skill never does.

## Install

Link this folder into `~/.claude/skills/uebersetzung/`, or let the runner read it by path. It needs the stimme skill's `stimme.md`.
