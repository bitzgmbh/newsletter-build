# ideen

The writing workshop for new ideas, stages 1 and 2 of the pipeline (decision 0038). `/ideen` files the new notes from the Element room "newsletter" as one idea each in `_ideen/` of the private repository, shows the backlog, and grills me in German, up to three rounds per idea, until the idea is parked, dropped or written up as a Rohentwurf in `_entwuerfe/`.

- `SKILL.md`: the skill.
- `scripts/ideen.py`: the mechanical part, standard library only: `eingang`, `liste`, `status`, `rohentwurf`, `notiz`. It never commits.
- `tests/test_ideen.py`: `python3 -m unittest discover skills/ideen/tests`.

The room is captured into archive.db by the same job as the other inbox rooms (role `newsletter`, larnsce/llm-wiki#303). The app shows the backlog read-only under Ideen.
