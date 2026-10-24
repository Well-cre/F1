from __future__ import annotations

import logging

from f1.pipelines.session_pipeline import SessionPipeline
from f1.storage import JsonDataSink


class FakeClient:
    def __init__(self, payloads: dict[str, list[dict[str, object]]]) -> None:
        self.payloads = payloads

    def get(
        self, endpoint: str, params: dict[str, object] | None = None
    ) -> list[dict[str, object]]:
        return self.payloads.get(endpoint, [])


def test_session_pipeline_writes_json_and_is_idempotent(tmp_path) -> None:
    payloads = {
        "sessions": [{"meeting_key": 1, "session_key": 2, "session_name": "Race"}],
        "drivers": [
            {
                "meeting_key": 1,
                "session_key": 2,
                "driver_number": 44,
                "name": "Hamilton",
            }
        ],
        "laps": [
            {"meeting_key": 1, "session_key": 2, "driver_number": 44, "lap_number": 1}
        ],
        "session_result": [
            {"meeting_key": 1, "session_key": 2, "position": 1, "driver_number": 44}
        ],
    }
    client = FakeClient(payloads)
    sink = JsonDataSink(tmp_path)
    pipeline = SessionPipeline(
        client=client, sink=sink, logger_instance=logging.getLogger("f1-test")
    )

    first = pipeline.run(meeting_key=1, session_key=2)
    second = pipeline.run(meeting_key=1, session_key=2)

    assert first["sessions"][0]["session_key"] == 2
    assert second["sessions"][0]["session_key"] == 2
    assert (tmp_path / "sessions.json").exists()
