# versand

Stage 10 from the terminal: the Buttondown drafts of an edition, created from the Quarto files, read back and checked.

## Why I use it

I write an edition in Quarto and send it from Buttondown. Between the two, things went wrong that I only saw in the preview: a chart that was a local path, line breaks in the middle of a paragraph, code in the English mail, an open editor tab that saved an old text over the new one. The skill names each of these and checks the draft for them, so I can send what the repository holds.

## What is in here

- `SKILL.md`: the steps (create, set the audience, check, update) and what the open editor tab does.
- The commands live in the app: `app/redaktion/entwurf.py` (`pruefen`, `aktualisieren`, `publikum`), on top of `app/redaktion/buttondown.py`.

## Install

Nothing beyond the app (`cd app && uv sync`) and the Buttondown key in the Keychain (service `bitz-buttondown`).
