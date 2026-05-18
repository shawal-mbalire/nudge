from __future__ import annotations

from collections import defaultdict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.utils import ENERGY_STYLE

console = Console()


def energy_text(energy: str) -> Text:
    return Text(energy.upper(), style=f"bold {ENERGY_STYLE[energy]}")


def status_text(status: str) -> Text:
    if status == "done":
        return Text("DONE", style="bold cyan")
    return Text("OPEN", style="bold white")


def print_task_tables(tasks: list[dict]) -> None:
    if not tasks:
        console.print("[yellow]No matching tasks.[/yellow]")
        return

    by_project: dict[str, list[dict]] = defaultdict(list)
    for task in tasks:
        by_project[task["project"]].append(task)

    summary = Table(title="Tasks by Project", header_style="bold magenta")
    summary.add_column("Project", style="bold")
    summary.add_column("Open", justify="right")
    summary.add_column("Done", justify="right")
    summary.add_column("Total", justify="right")

    for project in sorted(by_project):
        project_tasks = by_project[project]
        open_count = sum(1 for item in project_tasks if item["status"] == "open")
        done_count = sum(1 for item in project_tasks if item["status"] == "done")
        summary.add_row(
            project, str(open_count), str(done_count), str(len(project_tasks))
        )

    console.print(summary)

    for project in sorted(by_project):
        table = Table(
            title=f"Project: {project}",
            header_style="bold blue",
            show_lines=False,
        )
        table.add_column("ID", style="dim", justify="right")
        table.add_column("Task", overflow="fold")
        table.add_column("Energy / Effort", justify="center")
        table.add_column("Status", justify="center")

        for task in by_project[project]:
            table.add_row(
                str(task["id"]),
                task["desc"],
                energy_text(task["energy"]),
                status_text(task["status"]),
            )
        console.print(table)


def print_created_task(task: dict) -> None:
    energy_label = task["energy"].upper()
    energy_style = ENERGY_STYLE[task["energy"]]
    console.print(
        f"[bold green]Logged[/bold green] [cyan]#{task['id']}[/cyan] "
        f"for project [bold]{task['project']}[/bold] with "
        f"energy [bold {energy_style}]{energy_label}[/bold {energy_style}]."
    )


def print_marked_done(task_id: int) -> None:
    console.print(f"[bold cyan]Marked #{task_id} as done.[/bold cyan]")


def print_already_done(task_id: int) -> None:
    console.print(f"[cyan]Task #{task_id} is already done.[/cyan]")


def print_no_open_tasks(message: str) -> None:
    console.print(f"[yellow]{message}[/yellow]")


def print_guidance(task: dict) -> None:
    content = Text()
    content.append("Try this now\n", style="bold")
    content.append(f"#{task['id']} ", style="cyan")
    content.append(f"[{task['project']}] ", style="bold blue")
    content.append(task["desc"] + "\n")
    content.append("Energy / Effort: ", style="dim")
    content.append(task["energy"].upper(), style=f"bold {ENERGY_STYLE[task['energy']]}")
    console.print(
        Panel(
            content,
            title="Nudge",
            border_style=ENERGY_STYLE[task["energy"]],
            expand=False,
        )
    )
