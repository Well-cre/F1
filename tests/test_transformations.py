from __future__ import annotations

from f1.transforms import normalize_datetime, normalize_record, normalize_records


def test_normalize_datetime_moves_to_utc() -> None:
    value = "2024-08-02T12:34:56+02:00"

    assert normalize_datetime(value) == "2024-08-02T10:34:56+00:00"


def test_normalize_record_casts_identifier_fields() -> None:
    record = {"meeting_key": "123", "session_key": "456", "driver_number": "44"}

    normalized = normalize_record(record)

    assert normalized["meeting_key"] == 123
    assert normalized["session_key"] == 456
    assert normalized["driver_number"] == 44


def test_normalize_records_handles_sequence() -> None:
    records = [{"date": "2024-08-02T10:00:00Z"}, {"date": "2024-08-02T11:00:00+00:00"}]

    normalized = normalize_records(records)

    assert normalized[0]["date"] == "2024-08-02T10:00:00+00:00"
    assert normalized[1]["date"] == "2024-08-02T11:00:00+00:00"
