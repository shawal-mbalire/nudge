# nudge

Multi-component project with a Python CLI and an Angular landing page.

## Tech Stack

- **CLI**: Python 3.14+, Typer, Rich
- **Landing Page**: Angular 18, TypeScript
- **Task Runner**: just (justfile)

## Setup

```bash
# Install project-wide deps
just deps
```

### CLI

```bash
cd cli
uv sync
uv run main.py
```

### Landing Page

```bash
cd landing
npm install
ng serve
```
