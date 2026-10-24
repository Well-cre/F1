from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from f1.clients.openf1 import OpenF1Client
from f1.config import Settings

SESSION_FIELDS = (
    "meeting_key",
    "session_key",
    "session_name",
    "country_name",
    "year",
)


def format_sessions(records: Sequence[Mapping[str, Any]]) -> str:
    rows = [
        [str(record.get(field, "")) for field in SESSION_FIELDS] for record in records
    ]
    widths = [
        max(len(field), *(len(row[index]) for row in rows))
        for index, field in enumerate(SESSION_FIELDS)
    ]
    header = " | ".join(
        field.ljust(widths[index]) for index, field in enumerate(SESSION_FIELDS)
    )
    separator = "-+-".join("-" * width for width in widths)
    table_rows = [
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rows
    ]
    return "\n".join((header, separator, *table_rows))


def main() -> None:
    settings = Settings.from_env()
    with OpenF1Client(
        base_url=settings.base_url,
        timeout=settings.timeout_seconds,
    ) as client:
        sessions = client.get("sessions")

    if not sessions:
        print("Nenhuma sessão encontrada.")
        return

    print(format_sessions(sessions))


if __name__ == "__main__":
    main()
