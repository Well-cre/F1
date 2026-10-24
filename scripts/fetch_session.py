from __future__ import annotations

import argparse
import logging

from f1.clients.openf1 import OpenF1Client
from f1.config import Settings
from f1.pipelines.session_pipeline import SessionPipeline
from f1.storage import JsonDataSink

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extrai e persiste dados de uma sessão da OpenF1."
    )
    parser.add_argument(
        "--meeting-key",
        type=int,
        required=True,
        help="Identificador da etapa.",
    )
    parser.add_argument(
        "--session-key",
        type=int,
        default=None,
        help="Identificador da sessão.",
    )
    parser.add_argument(
        "--driver-number",
        type=int,
        default=None,
        help="Número do piloto opcional.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings.from_env()
    client = OpenF1Client(base_url=settings.base_url, timeout=settings.timeout_seconds)
    sink = JsonDataSink(settings.output_dir)
    pipeline = SessionPipeline(client=client, sink=sink)
    pipeline.run(
        meeting_key=args.meeting_key,
        session_key=args.session_key,
        driver_number=args.driver_number,
    )
    client.close()


if __name__ == "__main__":
    main()
