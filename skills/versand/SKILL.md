---
name: versand
disable-model-invocation: true
description: >-
  Stage 10 of a bitz edition from the terminal - create the Buttondown drafts
  (German and English) from the Quarto files, read them back, check them, set
  the audience and keep them current until Lars sends. Never sends. Use only
  when Lars invokes /versand or asks for the Buttondown draft of an edition.
---

# versand

The edition is written in Quarto, the mail goes out from Buttondown. This skill carries the text from one to the other and makes sure the draft in Buttondown is what the repository holds. Lars works in the terminal and the app shows where the edition stands (decision 0037). Sending is always his click in Buttondown.

## Before

- Stage 9 is done: `stand.py` shows "10 Versand" for the edition, dev and main of the private repository are pushed.
- The app runs (`curl -s <app_url>/api/ausgaben`). If not, ask Lars to start it in its own terminal with `cd app && uv run redaktion`.
- Every survey tag in the text (`{{ survey.<code> }}`) exists in Buttondown under exactly that code, one survey per language.

## Create the drafts

```sh
curl -s -X POST -d "sprache=de" <app_url>/ausgabe/<name>/versand
curl -s -X POST -d "sprache=en" <app_url>/ausgabe/<name>/versand
```

The app renders the edition in a copy of the repository, uploads the figures, creates the draft and writes its id into `pruefpunkte.md` ("Stufe 10 Versand: Entwurf in Buttondown ..."). One draft per language, once. A second POST makes a second draft; to change a draft, update it.

## Set the audience

```sh
cd app
uv run python -m redaktion.entwurf publikum <name>
uv run python -m redaktion.entwurf publikum <name> --en
```

A new draft has no filter and would go to everyone. The German mail goes to the answers Deutsch and Beide of the language question, the English one to English and Beide (decision 0036). Subscribers without an answer are Lars's two test accounts and get both. Tell Lars the number of recipients you expect from the subscriber list, and ask him to compare it with the number the Buttondown editor shows before he sends.

## Set the issue number

```sh
uv run python -m redaktion.entwurf nummer <name> <number>
uv run python -m redaktion.entwurf nummer <name> <number> --en
```

Buttondown counts every mail as an issue, so the German and the English mail of one edition would get two numbers. Both carry the number of the edition (Lars's choice of 12 November 2026). The number of the last edition is the `secondary_id` of its German mail.

## Check, every time

```sh
uv run python -m redaktion.entwurf pruefen <name>
uv run python -m redaktion.entwurf pruefen <name> --en
```

The command reads the draft back from Buttondown and checks what has gone wrong before:

- The body still starts with `<!-- buttondown-editor-mode: plaintext -->` and holds no `<br>`.
- No paragraph has a line end inside it. Buttondown shows such a line end as a break in the mail; the export renders with `wrap:none` for this reason.
- Every figure is uploaded. Quarto writes a figure with alt text as an HTML `<img>`; the export turns it into a markdown image first.
- No code, no TODO, no open shortcode. The English file is in the render list of `_quarto.yml` (`ausgaben/*/index-en.qmd`); outside it Quarto renders the file with its code visible.
- Subject and preview line match the header of the edition, and the audience is filtered.

Report the result to Lars with the link to each draft. A check that fails is fixed in the repository or in the export, never in the Buttondown editor.

## The open editor tab

The Buttondown editor saves what it holds. A tab that was open before an update writes its old copy over the draft a moment later, and in rich text mode it converts the body to HTML and keeps every old line end as `<br>`. On 12 November 2026 this put an older text back into the German draft.

- Before every update, ask Lars to close the editor tab of the draft, or to reload it right after the update without typing into it.
- After every update, run `pruefen` again and look at "Zuletzt geändert": a time later than your update means a tab has saved over it. Update once more after the tab is closed.
- The text is never edited in the Buttondown editor. A change goes into `index.qmd` or `index-en.qmd`, is committed, and reaches the draft through an update.
- The editor stays in markdown mode.

## Change after the draft exists

```sh
uv run python -m redaktion.entwurf aktualisieren <name>
uv run python -m redaktion.entwurf aktualisieren <name> --en
```

Renders the edition again, uploads the figures, and replaces body, subject and preview line of the existing draft; the audience stays. It runs the checks at the end. Commit the change in the private repository first, with a gate line in `pruefpunkte.md`, and push dev and main so the released state matches what goes out.

## Tests and surveys

A survey can only be answered from the mail. In the web archive Buttondown shows the answers as links that lead to "Umfrage nicht gefunden", by design, so the text of an edition with a survey says so in one sentence ("Die Umfrage lässt sich nur aus der Mail beantworten.", "The survey can only be answered from the email."). The comment field appears after the click on an answer, when the survey has free text switched on.

A subscriber answers a survey once. A second click lands on the sign-up page. Lars's test accounts receive the real mail with the live survey, so no click on an answer in a test mail.

## What this skill never does

- Send, schedule or publish an email. Changing the text of a sent mail (`aktualisieren`) changes its archive page and sends nothing; the check then reports the status `sent`, which is expected.
- Edit a draft in the Buttondown editor or write text that is not in the repository.
- Create a second draft where one exists for that language.
