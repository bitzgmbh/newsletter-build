# Skills per stage

First assessment of 2026-10-17, made at the AI Retreat. For each stage of the [pipeline map](map.qmd) it says whether an agent skill is needed and what it can build on. Built so far: the recherche skill for stage 4, the stimme skill for stage 5, the pruefung skill for stage 6, the grafiken skill for stage 7, the uebersetzung skill for stage 8, the verbreitung skill for stage 11, the runner for the gates and the app in [app/](../app/) (0028), next to the helpers already in [skills/](../skills/).

| # | Stage | Who | Skill needed? | Something to build on | Open decision | Crew role |
|---|---|---|---|---|---|---|
| 1 | Intake | Me | Yes, a light one: collect ideas into the backlog | The Element inbox room already captures notes from my phone | | |
| 2 | Select | Me | No, this is my call. A backlog view would help | A harvested list, like the control center in my vault | | |
| 3 | Rough draft | Me | No, the voice stays mine. At most, turn a spoken draft into text | Transcription I already run locally | | |
| 4 | Research | Agent | Yes | Built: [skills/recherche](../skills/recherche/), on my vault and the web | | Fachbibliothekar:in für Datenrecherche |
| 5 | Draft | Agent with me | Yes, the core skill: it proposes the outline as bullets, then reviews my text and records what it changes (0015) | Built: [skills/stimme](../skills/stimme/), on my plain-writing skill and [template.md](template.md) | | Wissenschaftsjournalist:in; Kursleiter:in für "Probier es selbst" |
| 6 | Checks | Agent | Yes: hard on facts, links and numbers without a source, hints on length, AI tells and the five personas (0016) | Built: [skills/pruefung](../skills/pruefung/), on my prose-lint skill | | Schlussredaktion und Faktencheck |
| 7 | Visuals | Agent with me | Yes: charts from code | Built: [skills/grafiken](../skills/grafiken/), on Quarto, ggplot2 and Observable Plot (decision 0008, [reproducibility.md](../reproducibility.md)) | | Datenjournalist:in |
| 8 | Translate | Agent | Yes, German to English, as its own email (0030) | Built: [skills/uebersetzung](../skills/uebersetzung/), on my plain-writing rules | 2 (who receives it) | Fachübersetzer:in |
| 9 | Approve | Me | No, a button in the app (0028) | [app/](../app/): Offenlegung, gate line, main fast-forwarded to dev | | |
| 10 | Send | Me, then Buttondown | No, the app creates the draft and I send in Buttondown (0029) | [app/](../app/) | | |
| 11 | Distribute | Agent, my yes | Yes: LinkedIn, Bluesky and Mastodon posts from the edition | Built: [skills/verbreitung](../skills/verbreitung/), on my plain-writing skill and clip | | Social Media Redakteur:in |
| 12 | Replies | Readers | Later: collect answers back into the backlog | The intake skill of stage 1 | | |
| 13 | Review | Me | Later, and a script rather than a skill: the signals from [concept.md](concept.md), read from Buttondown, the course sign-up form and the tagged links | [disclosure-summary](../skills/disclosure-summary/) shows the pattern: numbers from code | | |
| Gates | After stages 4 to 8 and 11 | Agent pings, I say yes | Yes, the runner: one shared step, a report, then wait (0014); decided in the app or with /redaktion (0034) | Built: [skills/runner](../skills/runner/) | | |
| All | Disclosure | Script | Yes, an edition version of disclosure-summary (0017) | Built: [skills/offenlegung](../skills/offenlegung/), on disclosure-summary | | |

## Reading of the table

- Each skill works from the crew role in its row ([concept.md](concept.md), Breite). The five reader personas from the same section read every draft at stage 6.
- About six skills to build: research, draft, checks, translate, distribute, and the disclosure block of an edition.
- Visuals and the gate step could be shared helpers rather than skills of their own.
- Stages 2, 3, 9 and 10 stay without a skill. Those are my choices, or a tool already does the job.
- Draft, checks and the runner come first: trial 1 needs them (decisions 0014 to 0016).
