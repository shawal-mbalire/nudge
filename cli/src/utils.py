from __future__ import annotations

import typer

ENERGY_LEVELS = ("low", "medium", "high")
ENERGY_RANK = {level: idx for idx, level in enumerate(ENERGY_LEVELS)}
ENERGY_STYLE = {"low": "green", "medium": "yellow", "high": "red"}


def normalize_energy(value: str) -> str:
    normalized = value.lower().strip()
    if normalized not in ENERGY_LEVELS:
        valid = ", ".join(ENERGY_LEVELS)
        raise typer.BadParameter(f"Energy must be one of: {valid}")
    return normalized
