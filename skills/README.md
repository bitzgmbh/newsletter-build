# Skills

Claude Code skills I use around the newsletter. Each folder holds one skill (`SKILL.md`) or one git hook, and a short README.

Every skill starts only when I invoke it with its slash command (`disable-model-invocation: true` in the frontmatter). Claude never starts one on its own. The runner still works, because it reads a stage's `SKILL.md` and follows it.

- [clip](clip/): copy a draft to the clipboard, ready to paste.
- [disclosure-summary](disclosure-summary/): add a "How AI was used" table to each pull request, counted from the commit trailers.
- [regent-trailer](regent-trailer/): link each agent commit to its re_gent session and step.
- [stimme](stimme/): outline an edition from my rough draft and review the text I wrote, without writing it (stage 5).
- [pruefung](pruefung/): check an edition, hard on facts, links and numbers, with hints on length, AI tells and the five personas (stage 6).
- [runner](runner/): move an edition by one stage, commit the output, report and record my yes (the gates, 0014).
- [redaktion](redaktion/): decide the open gate of an edition in Claude Code, with decision boxes; the app runs the stage (0034).
- [grafiken](grafiken/): the chart of an edition from data I name, static for the email and interactive for the website, from one file (stage 7).
- [versand](versand/): the Buttondown drafts of an edition from the terminal: create, set the audience and the issue number, read back and check, update (stage 10, 0037). It never sends.
- [verbreitung](verbreitung/): the posts that lead to an edition, one per channel, each standing on its own, with its own link parameter, and the image for a post (stage 11). I post them.
- [offenlegung](offenlegung/): the block "Offengelegt" of an edition, in sentences, built from its commits, trailers and stage files plus the sentences I confirmed (0017, 0020, 0040).
- [recherche](recherche/): sources for every claim in my rough draft, my own material, outside context and earlier editions (stage 4).
- [ideen](ideen/): file the notes from the Element room newsletter as ideas, show the backlog, and grill me in German until an idea is parked, dropped or a Rohentwurf (stages 1 and 2, 0038).
- [uebersetzung](uebersetzung/): the English version of an approved edition, for its own email (stage 8, 0030).

The app in [app/](../app/) starts the runner from a page per edition and takes my verdict there (0028). Which stages need a skill is assessed in [pipeline/skills.md](../pipeline/skills.md).
