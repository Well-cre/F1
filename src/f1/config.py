from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    """Configuração do projeto baseada em variáveis de ambiente."""

    base_url: str = field(
        default_factory=lambda: os.getenv(
            "OPENF1_BASE_URL",
            "https://api.openf1.org/v1/",
        )
    )
    timeout_seconds: float = field(
        default_factory=lambda: float(os.getenv("OPENF1_TIMEOUT_SECONDS", "20"))
    )
    output_dir: Path = field(
        default_factory=lambda: Path(os.getenv("F1_OUTPUT_DIR", "data"))
    )

    @classmethod
    def from_env(cls) -> Settings:
        settings = cls()
        settings.validate()
        return settings

    def validate(self) -> None:
        if not self.base_url or not self.base_url.startswith("http"):
            raise ValueError("OPENF1_BASE_URL deve ser uma URL HTTP válida.")
        if self.timeout_seconds <= 0:
            raise ValueError("OPENF1_TIMEOUT_SECONDS deve ser maior que zero.")
        self.output_dir.mkdir(parents=True, exist_ok=True)
