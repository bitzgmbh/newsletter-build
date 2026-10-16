# disclosure-summary

Every commit in this repository says who did the work, through its trailers (see [disclosure.md](../../disclosure.md)). This skill turns those trailers into a short table for each pull request: how many commits, and how many lines, were Claude-assisted, human-authored, mixed or unmarked.

I built it at the AI Retreat as the first piece of the AI disclosure side project. The test behind it: a reader of a pull request sees how AI was used without reading every commit.

The script is base R with no packages, so it runs wherever R and Git run:

```
Rscript skills/disclosure-summary/disclosure-summary.R [base] [head]
```

The defaults are `origin/main` and `HEAD`. Merge commits are skipped, and binary files count as zero lines.
