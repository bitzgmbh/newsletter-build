# verbreitung

The skill for stage 11 of the pipeline. It writes the posts that lead to an edition, one per channel, from the approved text. I post them myself.

## Why I use it

Each edition needs a post on LinkedIn, Bluesky and Mastodon, and each post has to carry on its own, because most people never click. The skill takes the one idea of the edition in my words, one concrete thing from it and the question to the reader, and puts the link last with the channel's own parameter, so I can see later which channel brought whom (measuring point 3 in `pipeline/concept.md`). It writes texts to paste. Posting stays with me, and nothing in a post goes beyond what the edition says.

## What is in here

- `SKILL.md`: the rules for every post and the output.
- `kanaele.md`: per channel the length, the tone, the link placement and the parameter.

## Install

Link this folder into `~/.claude/skills/verbreitung/`. It needs the stimme skill's `stimme.md` and `regeln.md`, and the clip skill to copy a post.
