from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx


class OpenF1Error(RuntimeError):
    """Erro de integração com a API OpenF1."""


class OpenF1Client:
    """Cliente HTTP para a API pública da OpenF1."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 20.0,
        session: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self._session = session or httpx.Client(timeout=self.timeout)

    def __enter__(self) -> OpenF1Client:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def close(self) -> None:
        if self._session is not None and not self._session.is_closed:
            self._session.close()

    def get(
        self,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        response = self._session.get(url, params=params)

        if response.status_code != httpx.codes.OK:
            detail = response.text[:200].replace("\n", " ")
            raise OpenF1Error(
                "Falha ao consultar "
                f"{endpoint}: status={response.status_code}; detalhe={detail}"
            )

        payload = response.json()
        if payload is None:
            return []
        if not isinstance(payload, list):
            raise OpenF1Error(
                "Resposta inválida de "
                f"{endpoint}: esperava lista, recebeu {type(payload).__name__}."
            )

        records = [item for item in payload if isinstance(item, dict)]
        if len(records) != len(payload):
            raise OpenF1Error(
                f"Resposta inválida de {endpoint}: alguns itens não são objetos JSON."
            )
        return records
