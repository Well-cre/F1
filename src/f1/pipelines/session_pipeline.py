from __future__ import annotations

import logging
from typing import Any

from f1.clients.openf1 import OpenF1Client
from f1.storage import JsonDataSink
from f1.transforms import normalize_records

logger = logging.getLogger(__name__)


class SessionPipeline:
    """Coordenador do fluxo de extração e carga para sessões de F1."""

    def __init__(
        self,
        client: OpenF1Client,
        sink: JsonDataSink,
        logger_instance: logging.Logger | None = None,
    ) -> None:
        self.client = client
        self.sink = sink
        self.logger = logger_instance or logger

    def fetch_resource(
        self,
        resource: str,
        *,
        meeting_key: int | None = None,
        session_key: int | None = None,
        driver_number: int | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if meeting_key is not None:
            params["meeting_key"] = meeting_key
        if session_key is not None:
            params["session_key"] = session_key
        if driver_number is not None:
            params["driver_number"] = driver_number

        self.logger.info("Consultando %s com filtros %s", resource, params)
        raw_records = self.client.get(resource, params=params)
        normalized = normalize_records(raw_records)
        self.logger.info("Consulta %s retornou %d registros", resource, len(normalized))
        return normalized

    def run(
        self,
        *,
        meeting_key: int,
        session_key: int | None = None,
        driver_number: int | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        resources = ["sessions", "drivers", "laps", "session_result"]
        results: dict[str, list[dict[str, Any]]] = {}

        for resource in resources:
            records = self.fetch_resource(
                resource,
                meeting_key=meeting_key,
                session_key=session_key,
                driver_number=driver_number,
            )
            stored_records = self.sink.write(resource, records)
            results[resource] = stored_records
            self.logger.info(
                "Carga concluída para %s com %d registros persistidos",
                resource,
                len(stored_records),
            )

        return results
