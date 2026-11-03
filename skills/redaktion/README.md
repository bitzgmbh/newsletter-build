# redaktion

The skill I use to decide the gates of an edition in Claude Code instead of on the app's page (decision 0034).

## Why I use it

The decision boxes in the terminal are quicker for me than the page: one question per point, a recommendation first, my free text where I need it. The app stays the map: it shows where each edition stands, runs the runner and keeps the log. This skill reads the open points from the app, asks me, sends my verdict back to the app, and follows the run to the next gate. Freigabe and the Buttondown draft stay buttons in the app.

## What is in here

- `SKILL.md`: how it picks the edition, builds the boxes and the verdict, and waits for the run.

## Install

Link this folder into `~/.claude/skills/redaktion/`. It needs the app running (`cd app && uv run redaktion`).
