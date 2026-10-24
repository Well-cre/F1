from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from f1.config import Settings

DATASETS = ("sessions", "drivers", "laps", "session_result")


def load_records(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open(encoding="utf-8") as data_file:
            payload = json.load(data_file)
    except OSError as exc:
        raise OSError(f"Não foi possível ler {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido em {path}: {exc}") from exc

    if not isinstance(payload, list):
        raise ValueError(f"Formato inválido em {path}: era esperada uma lista.")
    if any(not isinstance(record, dict) for record in payload):
        raise ValueError(
            f"Formato inválido em {path}: todos os itens devem ser objetos."
        )
    return payload


def build_session_summaries(
    sessions: list[dict[str, Any]],
    drivers: list[dict[str, Any]],
    laps: list[dict[str, Any]],
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    driver_names = {
        (record.get("session_key"), record.get("driver_number")): record.get(
            "name_acronym", str(record.get("driver_number", ""))
        )
        for record in drivers
    }
    summaries: list[dict[str, Any]] = []

    for session in sessions:
        session_key = session.get("session_key")
        session_results = [
            record for record in results if record.get("session_key") == session_key
        ]
        session_laps = [
            record
            for record in laps
            if record.get("session_key") == session_key
            and isinstance(record.get("lap_duration"), int | float)
        ]
        winner = min(
            session_results,
            key=lambda record: record.get("position", float("inf")),
            default={},
        )
        fastest_lap = min(
            session_laps,
            key=lambda record: record["lap_duration"],
            default={},
        )
        fastest_driver = fastest_lap.get("driver_number")

        summaries.append(
            {
                "session_key": session_key,
                "year": session.get("year"),
                "country": session.get("country_name"),
                "circuit": session.get("circuit_short_name"),
                "session": session.get("session_name"),
                "drivers": len(
                    {record.get("driver_number") for record in session_results}
                ),
                "winner": driver_names.get(
                    (session_key, winner.get("driver_number")), "—"
                ),
                "fastest_lap": fastest_lap.get("lap_duration"),
                "fastest_driver": driver_names.get((session_key, fastest_driver), "—"),
            }
        )

    return summaries


def build_driver_analysis(
    drivers: list[dict[str, Any]],
    laps: list[dict[str, Any]],
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    driver_info: dict[tuple[Any, int], dict[str, Any]] = {}
    fallback_driver_info: dict[int, dict[str, Any]] = {}
    for driver in drivers:
        driver_number = driver.get("driver_number")
        if isinstance(driver_number, int):
            driver_info.setdefault((driver.get("session_key"), driver_number), driver)
            fallback_driver_info.setdefault(driver_number, driver)

    fastest_by_session: dict[Any, dict[str, Any]] = {}
    for lap in laps:
        session_key = lap.get("session_key")
        duration = lap.get("lap_duration")
        if not isinstance(duration, int | float):
            continue
        current_fastest = fastest_by_session.get(session_key)
        if current_fastest is None or duration < current_fastest["lap_duration"]:
            fastest_by_session[session_key] = lap

    analysis: dict[str, dict[str, Any]] = {}
    for result in results:
        driver_number = result.get("driver_number")
        if not isinstance(driver_number, int):
            continue
        driver = driver_info.get(
            (result.get("session_key"), driver_number),
            fallback_driver_info.get(driver_number, {}),
        )
        driver_identity = driver.get("full_name") or driver.get("name_acronym")
        if not driver_identity:
            driver_identity = str(driver_number)
        summary = analysis.setdefault(
            driver_identity,
            {
                "driver_number": driver_number,
                "driver": driver.get("name_acronym", str(driver_number)),
                "country_code": driver.get("country_code", "—"),
                "team": driver.get("team_name", "—"),
                "points": 0.0,
                "wins": 0,
                "position_total": 0.0,
                "finishes": 0,
                "fastest_laps": 0,
            },
        )
        position = result.get("position")
        points = result.get("points")
        if isinstance(position, int | float):
            summary["position_total"] += position
            summary["finishes"] += 1
            if position == 1:
                summary["wins"] += 1
        if isinstance(points, int | float):
            summary["points"] += points
        fastest_lap = fastest_by_session.get(result.get("session_key"))
        if fastest_lap and fastest_lap.get("driver_number") == driver_number:
            summary["fastest_laps"] += 1

    def ranking_key(record: dict[str, Any]) -> tuple[float, int, float]:
        average_finish = (
            record["position_total"] / record["finishes"]
            if record["finishes"]
            else float("inf")
        )
        return (-record["points"], -record["wins"], average_finish)

    return [
        {
            **summary,
            "points": round(summary["points"], 1),
            "average_finish": round(summary["position_total"] / summary["finishes"], 2)
            if summary["finishes"]
            else None,
        }
        for summary in sorted(analysis.values(), key=ranking_key)
    ]


def main() -> None:
    st.set_page_config(page_title="F1 Dashboard", layout="wide")
    st.title("F1 Data Dashboard")
    st.caption("Visão comparativa de sessões, circuitos, pilotos e voltas.")

    output_dir = Settings.from_env().output_dir
    required_datasets = ("sessions", "drivers", "laps", "session_result")
    if not any(
        (output_dir / f"{dataset}.json").exists() for dataset in required_datasets
    ):
        st.info("Execute primeiro a coleta de dados")
        st.markdown("Liste as sessões disponíveis:")
        st.code("poetry run python scripts/list_sessions.py")
        st.markdown("Depois, colete os dados de uma sessão:")
        st.code(
            "poetry run python scripts/fetch_session.py --meeting-key X --session-key Y"
        )
        st.stop()

    try:
        datasets = {
            dataset: load_records(output_dir / f"{dataset}.json")
            for dataset in required_datasets
        }
    except (OSError, ValueError) as exc:
        st.error(str(exc))
        st.stop()

    sessions = datasets["sessions"]
    drivers = datasets["drivers"]
    laps = datasets["laps"]
    results = datasets["session_result"]
    session_summaries = build_session_summaries(sessions, drivers, laps, results)
    driver_analysis = build_driver_analysis(drivers, laps, results)
    all_fastest_laps = [
        {
            **summary,
            "fastest_lap_seconds": summary["fastest_lap"],
        }
        for summary in session_summaries
        if summary["fastest_lap"] is not None
    ]

    unique_circuits = {
        summary["circuit"] for summary in session_summaries if summary["circuit"]
    }
    unique_drivers = {
        (
            record.get("full_name") or record.get("name_acronym"),
            record.get("driver_number"),
        )
        for record in drivers
        if record.get("driver_number") is not None
    }
    fastest_overall = min(
        all_fastest_laps,
        key=lambda summary: summary["fastest_lap_seconds"],
        default=None,
    )
    metrics = st.columns(4)
    metrics[0].metric("Sessões", len(sessions))
    metrics[1].metric("Pistas", len(unique_circuits))
    metrics[2].metric("Pilotos", len(unique_drivers))
    metrics[3].metric(
        "Volta mais rápida",
        (f"{fastest_overall['fastest_lap_seconds']:.3f} s" if fastest_overall else "—"),
        fastest_overall["fastest_driver"] if fastest_overall else None,
    )

    sessions_tab, drivers_tab, laps_tab, raw_tab = st.tabs(
        ["Sessões e pistas", "Pilotos e resultados", "Voltas rápidas", "Dados brutos"]
    )

    with sessions_tab:
        st.subheader("Panorama das sessões")
        st.dataframe(session_summaries, width="stretch", hide_index=True)
        session_options = {
            (
                f"{summary['year']} · {summary['country']} — "
                f"{summary['circuit']} ({summary['session']})"
            ): summary["session_key"]
            for summary in session_summaries
        }
        if session_options:
            selected_label = st.selectbox(
                "Detalhar sessão",
                list(session_options),
            )
            selected_key = session_options[selected_label]
            selected_session = next(
                (
                    record
                    for record in sessions
                    if record.get("session_key") == selected_key
                ),
                {},
            )
            selected_results = sorted(
                (
                    record
                    for record in results
                    if record.get("session_key") == selected_key
                ),
                key=lambda record: record.get("position", float("inf")),
            )
            name_by_driver = {
                record.get("driver_number"): record.get("full_name")
                for record in drivers
                if record.get("session_key") == selected_key
            }
            result_table = [
                {
                    "Posição": record.get("position"),
                    "Piloto": name_by_driver.get(
                        record.get("driver_number"), record.get("driver_number")
                    ),
                    "Voltas": record.get("number_of_laps"),
                    "Pontos": record.get("points"),
                    "Diferença (s)": record.get("gap_to_leader"),
                    "Abandono": record.get("dnf"),
                }
                for record in selected_results
            ]
            st.subheader(
                f"Resultado — {selected_session.get('country_name', '')} / "
                f"{selected_session.get('circuit_short_name', '')}"
            )
            st.dataframe(result_table, width="stretch", hide_index=True)

    with drivers_tab:
        st.subheader("Desempenho acumulado dos pilotos")
        st.dataframe(
            [
                {
                    "Piloto": record["driver"],
                    "País": record["country_code"],
                    "Equipe": record["team"],
                    "Pontos": record["points"],
                    "Vitórias": record["wins"],
                    "Média de posição": record["average_finish"],
                    "Voltas mais rápidas": record["fastest_laps"],
                }
                for record in driver_analysis
            ],
            width="stretch",
            hide_index=True,
        )
        if driver_analysis:
            st.bar_chart(
                {
                    "Piloto": [record["driver"] for record in driver_analysis],
                    "Pontos": [record["points"] for record in driver_analysis],
                },
                x="Piloto",
                y="Pontos",
            )
            driver_options = {
                f"{record['driver']} — #{record['driver_number']}": record[
                    "driver_number"
                ]
                for record in driver_analysis
            }
            selected_driver = st.selectbox(
                "Detalhar piloto",
                list(driver_options),
            )
            selected_number = driver_options[selected_driver]
            session_by_key = {record.get("session_key"): record for record in sessions}
            personal_best_by_session: dict[Any, float] = {}
            for lap in laps:
                if lap.get("driver_number") != selected_number:
                    continue
                duration = lap.get("lap_duration")
                if not isinstance(duration, int | float):
                    continue
                session_key = lap.get("session_key")
                personal_best = personal_best_by_session.get(session_key)
                if personal_best is None or duration < personal_best:
                    personal_best_by_session[session_key] = duration
            driver_results = sorted(
                (
                    record
                    for record in results
                    if record.get("driver_number") == selected_number
                ),
                key=lambda record: session_by_key.get(
                    record.get("session_key"), {}
                ).get("date_start", ""),
            )
            st.subheader(f"Resultados por etapa — {selected_driver}")
            st.dataframe(
                [
                    {
                        "País": session_by_key.get(record.get("session_key"), {}).get(
                            "country_name", "—"
                        ),
                        "Pista": session_by_key.get(record.get("session_key"), {}).get(
                            "circuit_short_name", "—"
                        ),
                        "Posição": record.get("position"),
                        "Pontos": record.get("points"),
                        "Volta pessoal mais rápida (s)": personal_best_by_session.get(
                            record.get("session_key")
                        ),
                    }
                    for record in driver_results
                ],
                width="stretch",
                hide_index=True,
            )

    with laps_tab:
        st.subheader("Melhor volta de cada sessão")
        st.caption(
            "Os tempos variam conforme o traçado; compare voltas na mesma pista."
        )
        st.dataframe(
            [
                {
                    "País": record["country"],
                    "Pista": record["circuit"],
                    "Piloto": record["fastest_driver"],
                    "Volta (s)": record["fastest_lap_seconds"],
                }
                for record in all_fastest_laps
            ],
            width="stretch",
            hide_index=True,
        )
        if all_fastest_laps:
            st.bar_chart(
                {
                    "Pista": [
                        f"{record['country']} · {record['circuit']}"
                        for record in all_fastest_laps
                    ],
                    "Melhor volta (s)": [
                        record["fastest_lap_seconds"] for record in all_fastest_laps
                    ],
                },
                x="Pista",
                y="Melhor volta (s)",
            )

    with raw_tab:
        dataset = st.selectbox(
            "Dataset",
            DATASETS,
            format_func=lambda name: name.replace("_", " ").title(),
        )
        records = datasets[dataset]
        column_names = {key for record in records for key in record}
        empty_values = sum(
            value is None or value == ""
            for record in records
            for value in record.values()
        )
        metric_columns = st.columns(3)
        metric_columns[0].metric("Registros", len(records))
        metric_columns[1].metric("Colunas", len(column_names))
        metric_columns[2].metric("Valores vazios", empty_values)
        st.caption(f"Arquivo: {output_dir / f'{dataset}.json'}")
        st.dataframe(records, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
