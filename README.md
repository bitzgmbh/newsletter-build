# Zur Einsicht: the build log

This repository shows how I build the system behind my newsletter Zur Einsicht, step by step. I build it with AI agents, and the history shows where they helped.

I started it to prepare the AI Retreat in Bad Kohlgrub (16 to 18 October 2026), where the newsletter pipeline is my project. The first live edition is planned for mid November 2026.

## The project in three sentences

My summary for the retreat board, in German, the language the newsletter is written in first (decision 0009):

> Zur Einsicht ist mein persönlicher Newsletter für Leser:innen im deutschsprachigen Raum, und er bringt alle Teile meiner Arbeit zusammen, von Forschungsdaten an der ETH über meine Kurse und meine Arbeit mit KI bis zu meiner eigenen Firma. Er macht meine Kurse und künftige Veranstaltungen in der Schweiz bekannt, und regelmässige LinkedIn-Beiträge führen zu jeder Ausgabe. Am Retreat baue ich den Ablauf dahinter, von der ersten Idee über die Recherche bis zum Entwurf, mit festen Punkten, an denen ich selbst prüfe und die Stimme meine bleibt.

## How to read it

- `log/` has one short entry per work session, named by date.
- `decisions/` has one page per decision, with the options and my reasons. Open questions are in `decisions/README.md`, generated from `decisions/README.qmd`: a table as the overview, and one section per question for notes.
- `pipeline/map.qmd` shows the stages of the pipeline and where each one stands.
- `skills/` will hold the agent skills as they get built.
- The editions themselves live in a separate, private repository (decision 0005).
- `disclosure.md` explains how AI use is recorded in this repository.
- `reproducibility.md` lists the principles that keep figures, tables and numbers rebuildable from code.

## Current state

The pipeline exists as a map. No stage is built yet.

## What stays out

- Personal data, voice recordings and transcripts.
- Material from the retreat hosts. I link to it and write down only my own conclusions.
- Names and projects of other people, unless they agree.

## Who

Lars Schöbitz, bitz GmbH. Work happens on `dev` and is published on `main`.
