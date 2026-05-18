from __future__ import annotations

import random

import typer

from src.display import (
    print_already_done,
    print_created_task,
    print_guidance,
    print_marked_done,
    print_no_open_tasks,
    print_task_tables,
)
from src.storage import create_task, fetch_task_by_id, fetch_tasks, set_task_done
from src.utils import ENERGY_RANK, normalize_energy

app = typer.Typer(
    name="nudge",
    help="nudge: A low-pressure CLI tool to break choice paralysis",
    no_args_is_help=True,
)


def _pick_tasks(tasks: list[dict], max_energy: str, include_higher: bool) -> list[dict]:
    if include_higher:
        rank = ENERGY_RANK[max_energy]
        selected = [task for task in tasks if ENERGY_RANK[task["energy"]] <= rank]
    else:
        selected = [task for task in tasks if task["energy"] == max_energy]
    return [task for task in selected if task["status"] == "open"]


@app.command(name="new")
def new(
    desc: str = typer.Argument(..., help="Task description."),
    project: str = typer.Option("inbox", "--project", "-p", help="Project/group name."),
    energy: str = typer.Option(
        "low", "--energy", "-e", help="Energy needed: low, medium, high."
    ),
):
    task_desc = desc.strip()
    if not task_desc:
        raise typer.BadParameter("Task description cannot be empty.")

    row = create_task(task_desc, project.strip() or "inbox", energy)
    print_created_task(dict(row))


@app.command(name="browse")
@app.command(name="command", hidden=True)
def browse(
    energy: str = typer.Option("low", "--energy", "-e", help="Show tasks up to this energy."),
    exact: bool = typer.Option(
        False, "--exact", help="Only show tasks that match the exact energy."
    ),
    limit: int = typer.Option(10, "--limit", "-n", min=1, help="Max tasks to display."),
):
    max_energy = normalize_energy(energy)
    tasks = _pick_tasks(fetch_tasks(), max_energy=max_energy, include_higher=not exact)
    print_task_tables(tasks[:limit])


@app.command(name="list")
def list_tasks(
    project: str | None = typer.Option(None, "--project", "-p", help="Filter by project."),
    energy: str | None = typer.Option(None, "--energy", "-e", help="Filter by energy."),
    include_done: bool = typer.Option(False, "--all", help="Include completed tasks."),
):
    tasks = fetch_tasks(project=project, energy=energy, include_done=include_done)
    print_task_tables(tasks)


@app.command(name="done")
def done(
    task_id: int = typer.Argument(..., help="Task ID to mark complete."),
):
    task = fetch_task_by_id(task_id)
    if not task:
        raise typer.Exit(f"Task #{task_id} not found.")

    if task["status"] == "done":
        print_already_done(task_id)
        return

    set_task_done(task_id)
    print_marked_done(task_id)


@app.command(name="guide")
def guide(
    energy: str = typer.Option(
        "low", "--energy", "-e", help="Pick a task up to this energy."
    ),
):
    max_energy = normalize_energy(energy)
    tasks = _pick_tasks(fetch_tasks(), max_energy=max_energy, include_higher=True)

    if not tasks:
        print_no_open_tasks("No open tasks in this energy range.")
        return

    print_guidance(random.choice(tasks))


if __name__ == "__main__":
    app()
