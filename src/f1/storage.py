from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


class JsonDataSink:
    """Destino de dados em JSON com controle de idempotência."""

    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(
        self,
        resource_name: str,
        records: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        """Escreve registros em um arquivo JSON e evita duplicações."""
        target_path = self.output_dir / f"{resource_name}.json"
        existing_records: list[dict[str, Any]] = []
        if target_path.exists():
            with target_path.open("r", encoding="utf-8") as handle:
                loaded = json.load(handle)
                if isinstance(loaded, list):
                    existing_records = [
                        item for item in loaded if isinstance(item, dict)
                    ]

        merged_records: list[dict[str, Any]] = []
        seen_signatures: set[str] = set()

        for item in [*existing_records, *records]:
            signature = json.dumps(item, ensure_ascii=False, sort_keys=True)
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)
            merged_records.append(item)

        with target_path.open("w", encoding="utf-8") as handle:
            json.dump(merged_records, handle, ensure_ascii=False, indent=2)
            handle.write("\n")

        return merged_records
