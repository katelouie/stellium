"""
Typed data contracts for report sections.

Each section's `generate_data()` returns one of these types. Renderers
dispatch on the `"type"` Literal to determine how to format the data.

This replaces the previous informal `dict[str, Any]` contract and ensures
consistent key names across all sections and renderers.
"""

from typing import Any, Literal, TypedDict


class TableData(TypedDict):
    """Tabular data with headers and rows."""

    type: Literal["table"]
    headers: list[str]
    rows: list[list[Any]]


class KeyValueData(TypedDict):
    """Key-value pairs (e.g., Chart Overview, Moon Phase)."""

    type: Literal["key_value"]
    data: dict[str, str]


class TextData(TypedDict):
    """Plain text block."""

    type: Literal["text"]
    text: str


class SvgData(TypedDict):
    """Inline SVG content."""

    type: Literal["svg"]
    content: str


class SideBySideTablesData(TypedDict):
    """Multiple tables rendered side by side."""

    type: Literal["side_by_side_tables"]
    tables: list[dict[str, Any]]


class CompoundData(TypedDict):
    """Container for multiple sub-sections."""

    type: Literal["compound"]
    sections: list[tuple[str, "SectionData"]]


# The union of all section data types.
# Sections return one of these; renderers dispatch on the "type" key.
SectionData = (
    TableData | KeyValueData | TextData | SvgData | SideBySideTablesData | CompoundData
)
