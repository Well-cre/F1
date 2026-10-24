from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from f1 import dashboard
from f1.dashboard import (
    build_driver_analysis,
    build_session_summaries,
    load_records,
)


def test_load_records_reads_json_records(tmp_path) -> None:
    dataset_path = tmp_path / "sessions.json"
    dataset_path.write_text(
        json.dumps([{"session_key": 123, "session_name": "Race"}]),
        encoding="utf-8",
    )

    assert load_records(dataset_path) == [{"session_key": 123, "session_name": "Race"}]


def test_load_records_rejects_non_list_json(tmp_path) -> None:
    dataset_path = tmp_path / "sessions.json"
    dataset_path.write_text('{"session_key": 123}', encoding="utf-8")

    with pytest.raises(ValueError, match="era esperada uma lista"):
        load_records(dataset_path)


def test_build_session_summaries_finds_winner_and_fastest_lap() -> None:
    sessions = [
        {
            "session_key": 10,
            "year": 2023,
            "country_name": "Bahrain",
            "circuit_short_name": "Sakhir",
            "session_name": "Race",
        }
    ]
    drivers = [
        {"session_key": 10, "driver_number": 1, "name_acronym": "VER"},
        {"session_key": 10, "driver_number": 44, "name_acronym": "HAM"},
    ]
    laps = [
        {"session_key": 10, "driver_number": 1, "lap_duration": 95.1},
        {"session_key": 10, "driver_number": 44, "lap_duration": 94.8},
    ]
    results = [
        {"session_key": 10, "driver_number": 1, "position": 1},
        {"session_key": 10, "driver_number": 44, "position": 2},
    ]

    summary = build_session_summaries(sessions, drivers, laps, results)[0]

    assert summary["winner"] == "VER"
    assert summary["fastest_driver"] == "HAM"
    assert summary["fastest_lap"] == 94.8
    assert summary["drivers"] == 2


def test_build_driver_analysis_aggregates_points_wins_and_fastest_laps() -> None:
    drivers = [
        {
            "driver_number": 1,
            "name_acronym": "VER",
            "team_name": "Red Bull Racing",
        },
        {
            "driver_number": 44,
            "name_acronym": "HAM",
            "team_name": "Mercedes",
        },
    ]
    laps = [
        {"session_key": 10, "driver_number": 1, "lap_duration": 95.1},
        {"session_key": 11, "driver_number": 44, "lap_duration": 94.8},
    ]
    results = [
        {
            "session_key": 10,
            "driver_number": 1,
            "position": 1,
            "points": 25,
        },
        {
            "session_key": 10,
            "driver_number": 44,
            "position": 2,
            "points": 18,
        },
        {
            "session_key": 11,
            "driver_number": 1,
            "position": 2,
            "points": 18,
        },
        {
            "session_key": 11,
            "driver_number": 44,
            "position": 1,
            "points": 25,
        },
    ]

    analysis = build_driver_analysis(drivers, laps, results)

    assert [record["driver"] for record in analysis] == ["VER", "HAM"]
    assert analysis[0]["points"] == 43
    assert analysis[0]["wins"] == 1
    assert analysis[0]["average_finish"] == 1.5
    assert analysis[0]["fastest_laps"] == 1
    assert analysis[1]["fastest_laps"] == 1


def test_build_driver_analysis_distinguishes_same_number_between_seasons() -> None:
    drivers = [
        {
            "session_key": 10,
            "driver_number": 11,
            "full_name": "Sergio PEREZ",
            "name_acronym": "PER",
            "team_name": "Red Bull Racing",
        },
        {
            "session_key": 20,
            "driver_number": 11,
            "full_name": "Felipe DRUGOVICH",
            "name_acronym": "DRU",
            "country_code": "BRA",
            "team_name": "Aston Martin",
        },
    ]
    results = [
        {"session_key": 10, "driver_number": 11, "position": 2, "points": 18},
        {"session_key": 20, "driver_number": 11, "position": 1, "points": 25},
    ]

    analysis = build_driver_analysis(drivers, [], results)

    assert len(analysis) == 2
    assert {record["driver"] for record in analysis} == {"PER", "DRU"}
    assert {record["team"] for record in analysis} == {
        "Red Bull Racing",
        "Aston Martin",
    }
    brazilian_driver = next(record for record in analysis if record["driver"] == "DRU")
    assert brazilian_driver["country_code"] == "BRA"


def test_main_shows_collection_instructions_when_no_json_files_exist(
    tmp_path,
    monkeypatch,
) -> None:
    messages: list[str] = []
    commands: list[str] = []

    class DashboardStopped(Exception):
        pass

    def stop_dashboard() -> None:
        raise DashboardStopped

    monkeypatch.setattr(
        dashboard.Settings,
        "from_env",
        lambda: SimpleNamespace(output_dir=tmp_path),
    )
    monkeypatch.setattr(dashboard.st, "info", messages.append)
    monkeypatch.setattr(dashboard.st, "code", commands.append)
    monkeypatch.setattr(
        dashboard.st,
        "stop",
        stop_dashboard,
    )

    with pytest.raises(DashboardStopped):
        dashboard.main()

    assert messages == ["Execute primeiro a coleta de dados"]
    assert commands == [
        "poetry run python scripts/list_sessions.py",
        ("poetry run python scripts/fetch_session.py --meeting-key X --session-key Y"),
    ]
