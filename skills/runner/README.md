# runner

The shared step around the stage skills (decision 0014). It moves one edition by one stage per call, commits what the stage produced, pings me in Element with a link, and waits for my yes.

## Why I use it

Every agent stage ends with a gate, and I want each gate to look the same: one message with a link, one answer from me. The runner infers where an edition stands from the files in its folder, runs the skill for the next stage, commits only that stage's output on `dev`, and sends the ping. My answer goes into `pruefpunkte.md` next to the edition, one line per gate, with my feedback verbatim. That file is what the rule in `concept.md` reads before a gate may run without me. Stages without a skill yet stop with "Skill fehlt", so the pipeline runs end to end with its gaps named.

## What is in here

- `SKILL.md`: the stage order, the gate record, the ping, and what the runner never does.
- `scripts/stand.py`: infers the stage of an edition folder from its files and prints the last gate lines.

## Install

Link this folder into `~/.claude/skills/runner/`. It needs `~/.config/zur-einsicht.json` with the Matrix room and the path of the private repository; those values stay out of git.
