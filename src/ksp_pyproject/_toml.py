"""Applying a plain dict onto a tomlkit document without losing its formatting.

Each data class returns its own dict from ``dump()``. Assigning one of those
dicts straight onto a table would replace the node and take every comment in it
along with it, so ``merge`` walks the dict and writes leaves individually --
tomlkit keeps a line's comment and alignment across an in-place value swap.
"""

from typing import Any

import tomlkit
from tomlkit import TOMLDocument
from tomlkit.items import AoT, Table

TomlTable = TOMLDocument | Table


def subtable(table: TomlTable, key: str) -> Table:
    """Return ``table[key]``, creating an empty table if it isn't there yet."""
    existing = table.get(key)
    if existing is not None:
        return existing
    created = tomlkit.table()
    table[key] = created
    return created


def merge(table: TomlTable, data: dict[str, Any]) -> None:
    """Write ``data`` onto ``table``, disturbing as little as possible.

    ``None`` drops a key, since TOML has no null. Dropping takes the line's
    inline comment with it and leaves a commented-out line alone (tomlkit never
    saw that as a key). A standalone comment on the line *above* a dropped key
    stays put rather than being guessed at -- it may describe the section.
    """
    for key, value in data.items():
        if value is None:
            table.pop(key, None)
        elif isinstance(value, dict):
            merge(subtable(table, key), value)
        elif isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
            _merge_table_array(table, key, value)
        else:
            table[key] = value


def _merge_table_array(table: TomlTable, key: str, rows: list[dict[str, Any]]) -> None:
    """Reuse the existing array-of-tables entries so their comments survive."""
    entries: AoT | None = table.get(key)
    if entries is None:
        entries = tomlkit.aot()
        table[key] = entries

    while len(entries) > len(rows):
        del entries[-1]

    for index, row in enumerate(rows):
        if index < len(entries):
            merge(entries[index], row)
        else:
            entry = tomlkit.table()
            merge(entry, row)
            entries.append(entry)
