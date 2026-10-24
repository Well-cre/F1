from __future__ import annotations

import pytest

from f1.clients.openf1 import OpenF1Client, OpenF1Error


class DummyResponse:
    def __init__(
        self, status_code: int, payload: object | None = None, text: str = ""
    ) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self) -> object:
        if self._payload is None:
            return []
        return self._payload


class DummySession:
    def __init__(self, response: DummyResponse) -> None:
        self.response = response
        self.is_closed = False

    def get(self, url: str, params: object | None = None) -> DummyResponse:
        return self.response

    def close(self) -> None:
        self.is_closed = True


def test_openf1_client_returns_records() -> None:
    response = DummyResponse(200, [{"meeting_key": 123, "session_key": 456}])
    client = OpenF1Client("https://api.openf1.org/v1/", session=DummySession(response))

    assert client.get("sessions", params={"meeting_key": 123}) == [
        {"meeting_key": 123, "session_key": 456}
    ]


def test_openf1_client_raises_on_http_error() -> None:
    response = DummyResponse(500, text="error")
    client = OpenF1Client("https://api.openf1.org/v1/", session=DummySession(response))

    with pytest.raises(OpenF1Error, match="status=500"):
        client.get("sessions")
