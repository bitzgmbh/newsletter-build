# Decisions


<!-- Generated from README.qmd with quarto render. Edit README.qmd, not README.md. -->

## Made

- [0001 Owner and visibility](0001-owner-and-visibility.md)
- [0002 Skills live in this repository](0002-skills-in-this-repo.md)
- [0003 The map is code](0003-map-as-code.md)
- [0004 Editions are Quarto documents](0004-editions-are-quarto.md)
- [0005 Drafts live in a separate, private repository](0005-drafts-in-a-private-repo.md)
- [0006 What the website is for, and who sends the newsletter](0006-website-purpose-and-sender.md)
- [0007 How an approved edition is published](0007-publishing.md)
- [0008 D3 is for charts in editions](0008-d3-for-charts.md)
- [0009 Audience and title](0009-audience-and-title.md)
- [0010 Das Repository läuft auf Deutsch](0010-sprache.md)
- [0011 Domain und Registrar](0011-domain-und-registrar.md)
- [0012 Startseite](0012-startseite.md)
- [0013 Name des privaten Repositorys](0013-name-des-privaten-repositorys.md)
- [0014 Agenten](0014-agenten.md)
- [0015 Der Entwurf: Gliederung vom Agenten, Text von mir, Prüfung durch den Skill](0015-entwurf.md)
- [0016 Prüfungen](0016-pruefungen.md)
- [0017 Der Offenlegungsblock einer Ausgabe](0017-offenlegungsblock.md)
- [0018 Drei Blickwinkel als Hinweis in der Prüfung](0018-drei-blickwinkel.md)

## Open

The sheet I work through at the AI Retreat (16 to 18 October 2026). The table is the overview. Each open decision has its own section below, with room for my notes. When a decision is settled, it becomes a numbered file and its row and section leave this page.

| \# | Question | Current leaning |
|----|----|----|
| 1 | [What do English readers get from each edition?](#1-english-offer) | None yet |
| 2 | [Should my international network read Zur Einsicht, or only find it?](#2-english-audience) | Open until a few editions are out |
| 3 | [The English tagline](#3-tagline) | Draft only |
| 5 | [Website design](#5-website-design) | Leaning towards a new layout |
| 9 | [Blog](#9-blog) | Deep dive |
| 10 | [Edition template](#10-edition-template) | Draft in `pipeline/template.md` |
| 14 | [Prompt capture](#14-prompt-capture) | None yet |
| 15 | [License for this repository](#15-license-for-this-repository) | None yet |
| 16 | [Timeline for editions](#16-timeline) | A calendar at stage 2, with dates counted back from each send date |

## 1 English offer

- Question: what do English readers get from each edition?
- Options: a short English summary at the end; a full translation; English on LinkedIn only; an English version for selected editions.
- Current leaning: none yet.
- What would settle it: weighing the gate time per edition against what the English readers in question 2 need. The answer also decides whether stage 8 (Translate) stays on the map.

### Notes

## 2 English audience

- Question: should my international network read Zur Einsicht, or only find it?
- Options: read it; find it.
- Current leaning: open until a few editions are out.
- What would settle it: replies to the first editions show who actually reads.

### Notes

## 3 Tagline

- Question: which English tagline explains the title?
- Options: first draft, “for inspection: how the work is done, with AI, in the open”.
- Current leaning: draft only.
- What would settle it: trying it on people at the retreat.

### Notes

## 5 Website design

- Question: what does the website look like?
- Options: a completely new layout; the structure of the openwashdata.org website.
- Current leaning: a new layout.
- What would settle it:
  - What should a reader feel in the first five seconds, and how is that different from openwashdata.org?
  - Does “new” mean a new look on Quarto (a custom theme and page templates, which keeps decision 0004), or a new tool?
  - Which page do I design first: an edition, the start page, or a blog post?
  - Does Zur Einsicht get its own brand (colours, fonts, wordmark), or does it wait for the bitz brand?
  - How much time can design take before the first edition goes out?

### Notes

## 9 Blog

- Question: what is the blog post every four editions?
- Options: a round-up of all four editions; a deep dive on one.
- Current leaning: a deep dive on the edition that drew the most answers (see `pipeline/template.md`).
- What would settle it: feedback at the retreat.

### Notes

## 10 Edition template

- Question: which parts does every edition have, and how many words does each get?
- Options: the draft in `pipeline/template.md`.
- Current leaning: the draft.
- What would settle it: feedback at the retreat.

### Notes

## 14 Prompt capture

- Question: which tool records prompts for a reproducible pipeline?
- Options: re_gent; a curated prompts archive; other capture tools.
- Current leaning: none yet.
- What would settle it: a test on one edition.

### Notes

- 2026-10-17: both candidates are in use since the first pull request from the retreat. re_gent records every agent step in `.regent/` (not published), and the [regent-trailer](../skills/regent-trailer/) hook writes its session and step into each commit. The commit skill archives selected prompts word for word in `prompts/`, with a `Prompts:` trailer. Still open: whether the re_gent record gets a private server. Both feed the disclosure block of an edition (0017).

## 15 License for this repository

- Question: under which license is this repository published?
- Options: none yet.
- Current leaning: none yet.
- What would settle it: none yet.

### Notes

## 16 Timeline for editions

- Question: where in the pipeline does an edition get its send date, and who keeps the gates on time?
- Options: a calendar at stage 2 (Select) that I keep; a skill that counts back from the send date and reminds me in Element when a gate needs my yes; a separate planning stage before stage 1.
- Current leaning: a calendar at stage 2, with dates counted back from each send date. No separate stage.
- What would settle it: the first run of editions. Course sign-ups for rstatszh are due at the end of November 2026, so the welcome edition goes out on 3 November and the four editions of “Mehr als R” weekly from 10 November to 1 December, the course first; the trial editions become the live editions. The course page names no sign-up date; end of November is my own plan.

### Notes
