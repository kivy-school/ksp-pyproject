"""tomlkit primitives the data classes lean on.

Not a serialisation layer: every class states its own keys, its own example
values and its own child sections. These cover only what tomlkit itself makes
awkward -- creating a sub-table, sizing an array of tables, and writing a
commented-out line without turning it into a real key.
"""

import re
from typing import Any

import tomlkit
from tomlkit import TOMLDocument
from tomlkit.items import AoT, Comment, Table, Whitespace

TomlTable = TOMLDocument | Table


def subtable(table: TomlTable, key: str) -> Table:
    """Return ``table[key]``, creating an empty table if it isn't there yet."""
    existing = table.get(key)
    if existing is not None:
        return existing
    created = tomlkit.table()
    table[key] = created
    return created


def table_array(table: TomlTable, key: str, length: int) -> AoT:
    """Return ``table[key]`` as an array of tables holding exactly ``length`` entries.

    Existing entries are kept and reused so their comments survive; surplus ones
    are dropped and missing ones appended.
    """
    entries: AoT | None = table.get(key)
    if entries is None:
        entries = tomlkit.aot()
        table[key] = entries

    while len(entries) > length:
        del entries[-1]
    while len(entries) < length:
        entries.append(tomlkit.table())

    return entries


def render(key: str, value: Any) -> str:
    """Render ``key = value`` the way TOML would write it, on one line."""
    if isinstance(value, dict):
        inline = tomlkit.inline_table()
        inline.update(value)
        value = inline
    return tomlkit.dumps({key: value}).strip()


def _body(table: TomlTable) -> list[Any]:
    """The container body, for a TOMLDocument or a Table alike."""
    body = getattr(table, "body", None)
    if body is not None:
        return body
    return table.value.body


def _comments(table: TomlTable) -> list[str]:
    """Every comment attached to this table, standalone or trailing a key."""
    found: list[str] = []
    for _, item in _body(table):
        if isinstance(item, Whitespace):
            # .trivia raises on these rather than being absent
            continue
        if isinstance(item, Comment):
            found.append(item.trivia.comment)
            continue
        trivia = getattr(item, "trivia", None)
        if trivia is not None and trivia.comment:
            found.append(trivia.comment)
    return found


def is_mentioned(table: TomlTable, name: str) -> bool:
    """True if ``name`` is a live key here, or already named in any comment.

    Matched on word boundaries, so ``ios`` is not found inside ``scenarios``.
    Keeps scaffolding idempotent and stops it second-guessing a line the user
    deliberately commented out.
    """
    if name in table:
        return True

    pattern = re.compile(rf"\b{re.escape(name)}\b")
    for comment in _comments(table):
        if pattern.search(comment):
            return True

    return False


_HASH = re.compile(r"^#+\s*")


def _all_comments(table: TomlTable) -> list[str]:
    """Comments on this table and on every table nested under it.

    Reparsing moves a trailing comment into the body of whichever table it
    follows, so a section header written at the end of a document turns up
    inside the last table rather than at the root.
    """
    found = list(_comments(table))
    for _, item in _body(table):
        if isinstance(item, Table):
            found.extend(_all_comments(item))
        elif isinstance(item, AoT):
            for entry in item:
                found.extend(_all_comments(entry))
    return found


def declares_section(table: TomlTable, path: str) -> bool:
    """True if ``path`` already exists as a section, or as a commented-out header."""
    if path.rsplit(".", 1)[-1] in table:
        return True

    headers = {f"[{path}]", f"[[{path}]]"}
    for comment in _all_comments(table):
        if _HASH.sub("", comment).strip() in headers:
            return True

    return False


def comment_default(table: TomlTable, key: str, value: Any) -> None:
    """Document an unset optional as ``# key = value``."""
    if is_mentioned(table, key):
        return
    table.add(tomlkit.comment(render(key, value)))


def comment_section(table: TomlTable, path: str, values: dict[str, Any]) -> None:
    """Document a missing section as a commented-out ``[path]`` block."""
    if declares_section(table, path):
        return

    table.add(tomlkit.nl())
    table.add(tomlkit.comment(f"[{path}]"))
    for key, value in values.items():
        table.add(tomlkit.comment(render(key, value)))


def comment_table_array(table: TomlTable, path: str, values: dict[str, Any]) -> None:
    """Document a missing array of tables as a commented-out ``[[path]]`` block."""
    if declares_section(table, path):
        return

    table.add(tomlkit.nl())
    table.add(tomlkit.comment(f"[[{path}]]"))
    for key, value in values.items():
        table.add(tomlkit.comment(render(key, value)))
