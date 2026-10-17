# regent-trailer

A git hook that links commits to the re_gent record of the agent session they came from.

## Why I use it

re_gent records every agent step in `.regent/`, and git records the commits, but nothing connects the two. This hook adds two trailers to every commit made from a Claude Code session:

- `Regent-Session:` the re_gent session, always valid.
- `Regent-Step:` the last finished step of that session. A step is only written when a turn ends, so this is the turn before the one that runs the commit.

With them, `rgt log --session <id>` or `rgt show <step>` leads from a commit to the conversation behind it. The `.regent/` record is not published, so outside this machine the trailers point to nothing. That is accepted for this test.

Commits made outside a Claude Code session get no trailers. The hook never blocks a commit.

## Install

From the repository root:

```sh
ln -s ../../skills/regent-trailer/prepare-commit-msg .git/hooks/prepare-commit-msg
```

It needs `rgt` and `jq`.
