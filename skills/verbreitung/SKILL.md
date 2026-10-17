---
name: verbreitung
disable-model-invocation: true
description: >-
  Writes the posts that lead to an edition of Zur Einsicht, one per channel
  (LinkedIn, Bluesky, Mastodon), each standing on its own, from the approved
  edition. In German. Use when Lars asks for the posts of an edition, says
  "Posts für die Ausgabe", or the runner reaches stage 11. The skill writes
  texts to paste; Lars posts them himself.
---

# verbreitung

The skill works from one role: Social Media Redakteur:in (`pipeline/concept.md`, Breite). One post per channel, and each post carries on its own: someone who never clicks still gets the point of the edition. Stage 11 of the pipeline, after the edition is on the website.

## Files to read first

- The edition: `index.qmd` in the edition folder, or the file Lars names. The post takes its words from the edition, nothing else.
- `skills/stimme/stimme.md` and `skills/stimme/regeln.md`: Lars's voice and the German rules. They apply to posts as to editions.
- `kanaele.md` in this folder: the limits, tone and link placement per channel.

## Input

- The edition folder in `bitzgmbh/zur-einsicht`, `ausgaben/<JJJJ-MM-TT-kurzname>/`.
- The URL of the edition on the website: `https://zureinsicht.ch/ausgaben/<kurzname>/` once published. Before that, the placeholder `[URL]`.
- The series label from the front matter (`reihe`), if the edition has one.

If the edition has no text yet, stop. Posts come from the approved text, never from the outline.

## Rules for every post

1. It carries the one idea of the edition in Lars's words. Where a sentence of the edition carries the idea, quote it rather than paraphrase it.
2. It holds one concrete thing from the edition: the example, or the "Probier es selbst" step. Not both, and nothing the edition does not say.
3. It ends with the question to the reader from the edition, or a shortened form of it, before the link.
4. It works without the edition. Read the post alone: does it make the point? If not, rewrite it.
5. The link comes last, with the channel's parameter: `?ref=linkedin`, `?ref=bluesky`, `?ref=mastodon`. That is measuring point 3 in `concept.md`. No link shortener, no "Link in den Kommentaren".
6. The series label where the edition has one, as the first line: `Mehr als R (1/3)`.
7. The course is named only when the edition names it, and only as the edition does.
8. No call to subscribe in the post. The edition page has the form.
9. No emojis, no em dashes, no hashtags beyond at most two Lars already uses (see `kanaele.md`). Plain German in Swiss spelling, the Leser:innen form, du to the reader.
10. Within the channel's length in `kanaele.md`. On LinkedIn, the first 210 characters are what a reader sees before "mehr", so the hook goes first.

## Output

Write `verbreitung.md` into the edition folder:

- A first line naming the source file and the date.
- One section per channel, in this order: LinkedIn, Bluesky, Mastodon. Each with:
  - the post, ready to paste (Lars copies it with `/clip` and posts by hand),
  - the character count, counted with `python3 -c "import sys; print(len(open(sys.argv[1]).read()))"` on the post alone, or by eye from the text,
  - the proposed day and time: LinkedIn the morning after the send, Bluesky and Mastodon on the day of the send. Lars decides.
  - the link with its parameter.

Then stop. Stage 11 has a gate: the runner pings Lars with the first line of each post, and he says yes or changes a post.

## What this skill does not do

- Post anything. Lars posts.
- Invent a claim, a number or an example that is not in the edition.
- Change the edition.
- Link to Buttondown, to a platform copy of the edition, or to anything but the edition on the website (principle 1 of the map).
- Write a post for a channel not in `kanaele.md`.
