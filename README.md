# bitz: the build log

This repository shows how I build the system behind my newsletter bitz, step by step. bitz is written in German, for readers in Germany, Austria and Switzerland who work with data every day and feel far away from technical topics. Each edition has 500 to 700 words, and you can subscribe at <https://buttondown.com/bitz>. I build the system with AI agents, and the history shows where they helped.

Until 26 October 2026 the newsletter was called Zur Einsicht, which is now the name of one of its sections (decisions 0019 and 0020). The repositories were renamed the same day, from zur-einsicht-build and zur-einsicht to newsletter-build and newsletter (decision 0025).

## Current state

The welcome edition went out on 5 November 2026. Decision 0035 sets the rhythm after it: the next edition on Thursday 12 November 2026, then one every two weeks on Thursdays.

I work through an edition in the terminal with Claude Code, and the app in `app/` shows where each edition stands (decision 0037). The stages 1 and 2 have the skill `ideen` and the page Ideen in the app (0038). The stages 4 to 8, 10 and 11 each have a skill. The runner, which moves an edition one stage per call, still exists and runs only when I ask for it.

## How an edition gets made

The pipeline has 13 stages, drawn in [pipeline/map.qmd](pipeline/map.qmd). Today an edition takes this path:

1. Ideas arrive as short notes. The skill `ideen` files each one, asks me questions about it and ends with a parked idea, a dropped idea or a rough draft (stages 1 and 2, and the rough draft of stage 3).
2. I open a Claude Code session for the edition. The skills `recherche`, `stimme`, `pruefung`, `grafiken` and `uebersetzung` do the research, the outline and the text, the checks, the chart and the English version (stages 4 to 8). I decide every open point, and each decision is written down next to the edition.
3. The skill `offenlegung` writes the block "Offengelegt" from the commits of the edition and from sentences I confirm (decision 0040).
4. My yes is the push from `dev` to `main` in the private repository (stage 9).
5. The skill `versand` creates the Buttondown drafts in German and English, sets who receives which one and checks the drafts against the repository. I send them in Buttondown myself (stage 10).
6. The skill `verbreitung` writes the posts that lead to the edition. I post them (stage 11).

No skill starts on its own, and nothing goes out without my yes.

## How to read it

- [log/](log/) has one short entry per work session, named by date (in German, decision 0010).
- [decisions/](decisions/) has one page per decision, with the options and my reasons. [decisions/README.md](decisions/README.md) lists them and keeps the open questions. It is generated from `decisions/README.qmd`.
- [pipeline/map.qmd](pipeline/map.qmd) shows the stages of the pipeline and where each one stands.
- [pipeline/concept.md](pipeline/concept.md) holds the goal, the assumptions I test and the crew behind each stage (in German).
- [pipeline/template.md](pipeline/template.md) holds the parts of an edition and their word counts. [pipeline/skills.md](pipeline/skills.md) says which stage needs a skill, and [pipeline/trials.md](pipeline/trials.md) describes the first editions as trial runs.
- [skills/](skills/) holds the Claude Code skills and one git hook. The list is below.
- [app/](app/) holds Redaktion, a local app that shows where each edition stands and lists the ideas. It also holds the code that turns an edition into a Buttondown draft (decisions 0028, 0029 and 0037).
- [prompts/](prompts/) archives, word for word, prompts behind some Claude-assisted commits, up to 3 November 2026.
- [disclosure.md](disclosure.md) explains how AI use is recorded in this repository. Since decision 0040, the block "Offengelegt" at the end of an edition links to it.
- [reproducibility.md](reproducibility.md) lists the principles that keep figures, tables and numbers rebuildable from code.
- The editions and the website live in the private repository `bitzgmbh/newsletter` (decisions 0005 and 0025).

## Skills

| Skill | Stage | What it does |
|---|---|---|
| [ideen](skills/ideen/) | 1 and 2 | Files new notes as ideas, shows the backlog and asks me questions until an idea is parked, dropped or a rough draft |
| [recherche](skills/recherche/) | 4 | Finds sources for every claim in my rough draft |
| [stimme](skills/stimme/) | 5 | Outlines the edition, writes the text from the outline I approved and reviews it |
| [pruefung](skills/pruefung/) | 6 | Checks facts, links and numbers, says whether linked publications are open access, and gives hints on length and AI tells |
| [grafiken](skills/grafiken/) | 7 | Makes the chart of an edition from code, in the colours and the font of the bitz brand (decision 0039) |
| [uebersetzung](skills/uebersetzung/) | 8 | Writes the English version, sent as its own email |
| [versand](skills/versand/) | 10 | Creates, checks and updates the Buttondown drafts. It never sends |
| [verbreitung](skills/verbreitung/) | 11 | Writes the posts that lead to an edition, one per channel |
| [offenlegung](skills/offenlegung/) | all | Writes the block "Offengelegt" of an edition |
| [runner](skills/runner/) | gates | Moves an edition by one stage and records my yes, on request |
| [redaktion](skills/redaktion/) | gates | Asks me the open points of a runner run as decision boxes |
| [disclosure-summary](skills/disclosure-summary/) | this repository | Adds the table "How AI was used" to each pull request |
| [regent-trailer](skills/regent-trailer/) | this repository | A git hook that links each agent commit to its session record |
| [clip](skills/clip/) | helper | Copies a draft to the clipboard |

## Running it

An edition cannot be built from this repository alone, because the editions live in the private repository. These parts run on their own:

- The app: `cd app && uv run redaktion`, then open <http://127.0.0.1:8765>. It reads the path of the private repository from `~/.config/bitz-newsletter.json`. Details are in [app/README.md](app/README.md).
- A skill: link or copy its folder into `~/.claude/skills/` and call it with its slash command in Claude Code. The README in each skill folder says what the skill needs.
- The tests: `cd app && uv run python -m unittest discover tests`, and from the top of the repository `python3 -m unittest discover skills/runner/tests` and `python3 -m unittest discover skills/ideen/tests`.
- The map: `quarto render pipeline/map.qmd`.
- The list of decisions: `quarto render decisions/README.qmd`.

## Where it started

I started this repository to prepare the AI Retreat in Bad Kohlgrub (16 to 18 October 2026), where the newsletter pipeline was my project. My summary for the retreat board of October 2026, in German and under the old name:

> Zur Einsicht ist mein persönlicher Newsletter für Leser:innen im deutschsprachigen Raum, und er bringt alle Teile meiner Arbeit zusammen, von Forschungsdaten an der ETH über meine Kurse und meine Arbeit mit KI bis zu meiner eigenen Firma. Er macht meine Kurse und künftige Veranstaltungen in der Schweiz bekannt, und regelmässige LinkedIn-Beiträge führen zu jeder Ausgabe. Am Retreat baue ich den Ablauf dahinter, von der ersten Idee über die Recherche bis zum Entwurf, mit festen Punkten, an denen ich selbst prüfe und die Stimme meine bleibt.

## What stays out

- Personal data, voice recordings and transcripts.
- Material from the retreat hosts. I link to it and write down only my own conclusions.
- Names and projects of other people, unless they agree.

## Who

Lars Schöbitz, bitz GmbH. Work happens on `dev` and is published on `main`. This repository has no license yet (open question 15 in `decisions/README.md`).
