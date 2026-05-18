# nudge

A low-pressure CLI for capturing tasks and browsing them by energy level.

Tasks are stored in SQLite at `~/.nudge.db` (legacy `~/.nudge.json` is migrated automatically on first run).

## Commands

- `nudge new "desc" -p inbox -e low` add a task (`low|medium|high`)
- `nudge list` list open tasks
- `nudge browse -e low` browse tasks at or below an energy level
- `nudge guide -e low` pick one task suggestion for your current energy
- `nudge done 3` mark a task complete

`list` and `browse` render colorful tables grouped per project, including an **Energy / Effort** column.
