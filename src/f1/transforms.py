from __future__ import annotations

import datetime as dt
from collections.abc import Mapping, Sequence
from typing import Any


def normalize_datetime(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, dt.datetime):
        aware_value = (
            value if value.tzinfo is not None else value.replace(tzinfo=dt.UTC)
        )
        return aware_value.astimezone(dt.UTC).isoformat()
    if isinstance(value, str):
        candidate = value.strip()
        if not candidate:
            return None
        try:
            parsed = dt.datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError:
            return candidate
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.UTC)
        return parsed.astimezone(dt.UTC).isoformat()
    return None


def normalize_record(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in record.items():
        if key in {"meeting_key", "session_key", "driver_number", "lap_number", "year"}:
            if value in (None, ""):
                normalized[key] = None
            else:
                try:
                    normalized[key] = int(value)
                except (TypeError, ValueError):
                    normalized[key] = value
        elif key in {
            "date",
            "date_start",
            "date_end",
            "session_start",
            "session_end",
            "timestamp",
        }:
            normalized[key] = normalize_datetime(value)
        elif isinstance(value, str):
            normalized[key] = value.strip()
        else:
            normalized[key] = value
    return normalized


def normalize_records(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [normalize_record(record) for record in records]
