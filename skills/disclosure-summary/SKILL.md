---
name: disclosure-summary
disable-model-invocation: true
description: >-
  Add a "How AI was used" section to the body of a pull request, counted
  from the commit trailers Assisted-by and Human-authored. Use whenever a
  pull request is opened or updated in this repository, or when the user
  asks how much of a branch was written with AI.
---

# disclosure-summary

Run from the repository root, after `dev` is pushed:

```
Rscript skills/disclosure-summary/disclosure-summary.R origin/main dev
```

Paste the printed section, unchanged, at the end of the pull request body, after the Summary. When the pull request gets new commits, run it again and replace the section.

- The numbers come from the script only. Never type, round or reword them.
- If the script stops with an error, say so and leave the section out. Never write a section by hand.
- Raw trailers (`Assisted-by:`, `Prompts:`) still stay out of the pull request body. Only this summary goes in.
