# How AI was used

I build this system together with Claude (Claude Code). Every commit says who did the work:

- `Assisted-by: Claude <model>` means Claude wrote or changed it.
- `Human-authored: true` means I wrote or changed it.
- A commit with both is mixed work.

Claude-assisted commits can carry more trailers:

- `Prompts:` lists the prompts behind the change. Each one is archived word for word in `prompts/`, one file per prompt.
- `Regent-Session:` and `Regent-Step:` point to the re_gent record of the agent session on my machine, written by the [regent-trailer](skills/regent-trailer/) hook. That record is not published, so these two trailers resolve only there. Each edition carries the same idea as a block built by the [offenlegung](skills/offenlegung/) skill from the commits of that edition.

The ideas, the decisions and the final yes on every edition are mine.

To count them yourself:

```
git log --grep='^Assisted-by:' --oneline
git log --grep='^Human-authored:' --oneline
```

Each pull request into `main` ends with a "How AI was used" table built from these trailers by the [disclosure-summary](skills/disclosure-summary/) skill.

A summary per phase follows here after the retreat.
