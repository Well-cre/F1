from __future__ import annotations

from scripts.list_sessions import format_sessions


def test_format_sessions_includes_requested_fields() -> None:
    records = [
        {
            "meeting_key": 123,
            "session_key": 456,
            "session_name": "Race",
            "country_name": "Brazil",
            "year": 2024,
        }
    ]

    output = format_sessions(records)

    assert output.splitlines()[0] == (
        "meeting_key | session_key | session_name | country_name | year"
    )
    assert "123" in output
    assert "456" in output
    assert "Race" in output
    assert "Brazil" in output
    assert "2024" in output
