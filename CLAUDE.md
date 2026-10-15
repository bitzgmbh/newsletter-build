# Agent guidance for this repository

This is a public repository. Everything committed here is published.

## Log entries

One file per work session in `log/`, named `YYYY-MM-DD.md` (add `-2` for a second session on the same day). Keep each entry short, four labelled bullets, more lines only when needed:

```
# YYYY-MM-DD

- Did:
- Learned:
- Decided:
- Next:
```

Write in plain English. Leave a bullet empty with "nothing" rather than padding it.

## Decisions

One file per decision in `decisions/`, numbered `NNNN-short-name.md`, with Question, Options, Choice, Why and Date. When a decision is made, remove its row and its section from the open part of `decisions/README.qmd`. Then run `quarto render decisions/README.qmd` and commit `README.qmd` together with the generated `README.md`. Never edit `decisions/README.md` by hand.

## Never commit

- Personal data, voice recordings, transcripts or references to them.
- Content copied from the retreat board or other material of the hosts.
- Names or projects of other participants without their consent.
- Secrets. The gitleaks workflow scans every push.

## Commits

Use the authorship trailers (`Assisted-by:` for Claude-touched work, `Human-authored: true` for my own work, both for mixed work). `disclosure.md` is built from them.
