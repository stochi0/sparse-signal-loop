"""Shared helpers for factorial / grid experiment CLIs."""

from __future__ import annotations

from typing import Protocol, TypeVar


class CellWithSlug(Protocol):
    def slug(self) -> str: ...


T = TypeVar("T", bound=CellWithSlug)


def parse_cell_filter(slugs: str | None, cells: list[T]) -> list[T]:
    """Return all ``cells`` when ``slugs`` is empty; otherwise preserve comma-separated order."""
    if not slugs:
        return list(cells)
    order = [s.strip() for s in slugs.split(",") if s.strip()]
    by_slug = {c.slug(): c for c in cells}
    missing = set(order) - set(by_slug.keys())
    if missing:
        raise ValueError(f"Unknown cell slug(s): {sorted(missing)}. Valid: {sorted(by_slug)}")
    return [by_slug[s] for s in order]
