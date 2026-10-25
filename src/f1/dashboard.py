from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from f1.config import Settings

DATASETS = ("sessions", "drivers", "laps", "session_result")
ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_PATH = ASSETS_DIR / "f1-data-logo.svg"
FAVICON_PATH = ASSETS_DIR / "f1-data-favicon.svg"
CHART_COLORS = ("#e10600", "#ffb000", "#00d2be", "#6c8cff", "#a78bfa")

DASHBOARD_THEME = """
<style>
    @keyframes f1-dashboard-enter {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    [data-testid="stMainBlockContainer"] {
        animation: f1-dashboard-enter 420ms ease-out both;
    }
    div[data-testid="stMetric"] {
        transition: transform 180ms ease, border-color 180ms ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(225, 6, 0, 0.65);
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }
</style>
"""


@st.cache_data(show_spinner=False, max_entries=4, ttl="5m")
def load_dataset_bundle(
    output_dir: Path, required_datasets: tuple[str, ...]
) -> dict[str, list[dict[str, Any]]]:
    return {
        dataset: load_records(output_dir / f"{dataset}.json")
        for dataset in required_datasets
    }


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
    results_by_session: dict[Any, list[dict[str, Any]]] = {}
    laps_by_session: dict[Any, list[dict[str, Any]]] = {}
    for record in results:
        results_by_session.setdefault(record.get("session_key"), []).append(record)
    for record in laps:
        if isinstance(record.get("lap_duration"), int | float):
            laps_by_session.setdefault(record.get("session_key"), []).append(record)

    summaries: list[dict[str, Any]] = []

    for session in sessions:
        session_key = session.get("session_key")
        session_results = results_by_session.get(session_key, [])
        session_laps = laps_by_session.get(session_key, [])
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


@st.cache_data(show_spinner=False, max_entries=4)
def build_dashboard_state(
    datasets: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
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
    fastest_overall = min(
        all_fastest_laps,
        key=lambda summary: summary["fastest_lap_seconds"],
        default=None,
    )
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
    return {
        "sessions": sessions,
        "drivers": drivers,
        "laps": laps,
        "results": results,
        "session_result": results,
        "session_summaries": session_summaries,
        "driver_analysis": driver_analysis,
        "all_fastest_laps": all_fastest_laps,
        "unique_circuits": unique_circuits,
        "unique_drivers": unique_drivers,
        "fastest_overall": fastest_overall,
    }


def render_metric_cards(state: dict[str, Any]) -> None:
    fastest_overall = state["fastest_overall"]
    with st.container(horizontal=True):
        st.metric("Sessões", len(state["sessions"]), border=True)
        st.metric("Pistas", len(state["unique_circuits"]), border=True)
        st.metric("Pilotos", len(state["unique_drivers"]), border=True)
        st.metric(
            "Volta mais rápida",
            (
                f"{fastest_overall['fastest_lap_seconds']:.3f} s"
                if fastest_overall is not None
                else "—"
            ),
            fastest_overall["fastest_driver"] if fastest_overall else None,
            border=True,
        )


def render_data_table(data: list[dict[str, Any]], alt: str) -> None:
    st.dataframe(data, width="stretch", hide_index=True, alt=alt)


def style_plotly_chart(figure: go.Figure, *, height: int = 420) -> go.Figure:
    figure.update_layout(
        template="plotly_dark",
        height=height,
        margin={"l": 12, "r": 12, "t": 32, "b": 12},
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        font={"family": "Inter, sans-serif", "color": "#e5e7eb"},
        hoverlabel={
            "bgcolor": "#151b25",
            "bordercolor": "#344052",
            "font": {"color": "#f8fafc"},
        },
    )
    figure.update_xaxes(showgrid=False, zeroline=False)
    figure.update_yaxes(
        gridcolor="rgba(148, 163, 184, 0.14)",
        zeroline=False,
    )
    return figure


def render_sessions_section(state: dict[str, Any]) -> None:
    st.subheader("Panorama das sessões")
    render_data_table(
        state["session_summaries"],
        "Resumo das sessões, vencedores e melhores voltas",
    )

    session_options = {
        (
            f"{summary['year']} · {summary['country']} — "
            f"{summary['circuit']} ({summary['session']})"
        ): summary["session_key"]
        for summary in state["session_summaries"]
    }

    if not session_options:
        return

    selected_label = st.selectbox("Detalhar sessão", list(session_options))
    selected_key = session_options[selected_label]
    selected_session = next(
        (
            record
            for record in state["sessions"]
            if record.get("session_key") == selected_key
        ),
        {},
    )
    selected_results = sorted(
        (
            record
            for record in state["results"]
            if record.get("session_key") == selected_key
        ),
        key=lambda record: record.get("position", float("inf")),
    )
    name_by_driver = {
        record.get("driver_number"): record.get("full_name")
        for record in state["drivers"]
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
    render_data_table(result_table, "Classificação da sessão selecionada")


def render_drivers_section(state: dict[str, Any]) -> None:
    st.subheader("Desempenho acumulado dos pilotos")
    render_data_table(
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
            for record in state["driver_analysis"]
        ],
        "Pontuação, vitórias e desempenho acumulado dos pilotos",
    )

    if not state["driver_analysis"]:
        return

    driver_chart = px.bar(
        state["driver_analysis"],
        x="points",
        y="driver",
        color="team",
        orientation="h",
        hover_data={
            "wins": True,
            "average_finish": True,
            "fastest_laps": True,
            "team": True,
        },
        labels={
            "points": "Pontos",
            "driver": "Piloto",
            "team": "Equipe",
            "wins": "Vitórias",
            "average_finish": "Média de posição",
            "fastest_laps": "Voltas mais rápidas",
        },
        color_discrete_sequence=CHART_COLORS,
    )
    driver_chart.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="Pontos",
        yaxis_title=None,
        legend_title="Equipe",
    )
    st.plotly_chart(
        style_plotly_chart(driver_chart, height=480),
        width="stretch",
        theme=None,
        config={"displayModeBar": False, "responsive": True},
        alt="Pontuação acumulada por piloto, agrupada por equipe",
    )

    driver_options = {
        f"{record['driver']} — #{record['driver_number']}": record["driver_number"]
        for record in state["driver_analysis"]
    }
    selected_driver = st.selectbox("Detalhar piloto", list(driver_options))
    selected_number = driver_options[selected_driver]
    session_by_key = {record.get("session_key"): record for record in state["sessions"]}
    personal_best_by_session: dict[Any, float] = {}
    for lap in state["laps"]:
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
            for record in state["results"]
            if record.get("driver_number") == selected_number
        ),
        key=lambda record: session_by_key.get(record.get("session_key"), {}).get(
            "date_start", ""
        ),
    )
    st.subheader(f"Resultados por etapa — {selected_driver}")
    render_data_table(
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
        "Resultados do piloto por etapa e melhor volta pessoal",
    )


def render_laps_section(state: dict[str, Any]) -> None:
    st.subheader("Melhor volta de cada sessão")
    st.caption("Os tempos variam conforme o traçado; compare voltas na mesma pista.")
    render_data_table(
        [
            {
                "País": record["country"],
                "Pista": record["circuit"],
                "Piloto": record["fastest_driver"],
                "Volta (s)": record["fastest_lap_seconds"],
            }
            for record in state["all_fastest_laps"]
        ],
        "Melhor volta registrada por sessão, com pista e piloto",
    )
    if state["all_fastest_laps"]:
        lap_chart = px.scatter(
            state["all_fastest_laps"],
            x="circuit",
            y="fastest_lap_seconds",
            color="fastest_driver",
            hover_name="country",
            hover_data={"session": True, "year": True},
            labels={
                "circuit": "Circuito",
                "fastest_lap_seconds": "Tempo (s)",
                "fastest_driver": "Piloto",
                "session": "Sessão",
                "year": "Temporada",
            },
            color_discrete_sequence=CHART_COLORS,
        )
        lap_chart.update_traces(
            marker={"size": 11, "line": {"width": 1, "color": "#f8fafc"}},
            mode="markers",
        )
        lap_chart.update_layout(
            xaxis_title="Circuito",
            yaxis_title="Melhor volta (s)",
            legend_title="Piloto",
        )
        st.plotly_chart(
            style_plotly_chart(lap_chart),
            width="stretch",
            theme=None,
            config={"displayModeBar": False, "responsive": True},
            alt="Tempos das melhores voltas por circuito e piloto",
        )


def render_raw_section(state: dict[str, Any]) -> None:
    dataset = st.selectbox(
        "Dataset",
        DATASETS,
        format_func=lambda name: name.replace("_", " ").title(),
    )
    records = state[dataset]
    column_names = {key for record in records for key in record}
    empty_values = sum(
        value is None or value == "" for record in records for value in record.values()
    )
    with st.container(horizontal=True):
        st.metric("Registros", len(records), border=True)
        st.metric("Colunas", len(column_names), border=True)
        st.metric("Valores vazios", empty_values, border=True)
    st.caption(f"Arquivo: {Settings.from_env().output_dir / f'{dataset}.json'}")
    render_data_table(records, f"Registros do dataset {dataset}")


def main() -> None:
    st.set_page_config(
        page_title="F1 Race Intelligence",
        page_icon=str(FAVICON_PATH),
        layout="wide",
        initial_sidebar_state="auto",
    )
    st.logo(str(LOGO_PATH), size="medium", icon_image=str(FAVICON_PATH))
    st.html(DASHBOARD_THEME)
    st.badge(
        "Race intelligence",
        icon=":material/speed:",
        color="red",
    )
    st.title("F1 Race Intelligence")
    st.caption("Dados de corrida, transformados em decisões mais rápidas.")

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
        datasets = load_dataset_bundle(output_dir, required_datasets)
    except (OSError, ValueError) as exc:
        st.error(str(exc))
        st.stop()

    state = build_dashboard_state(datasets)
    render_metric_cards(state)

    st.sidebar.subheader("Navegação")
    navigation = st.sidebar.radio(
        "Escolha uma seção",
        ["Resumo", "Sessões", "Pilotos", "Voltas", "Dados brutos"],
        captions=[
            "Indicadores e panorama",
            "Etapas e classificações",
            "Pontuação e desempenho",
            "Ritmo por circuito",
            "Arquivos de origem",
        ],
        index=0,
        label_visibility="collapsed",
    )
    st.sidebar.button(
        "Atualizar dados",
        icon=":material/refresh:",
        width="stretch",
        on_click=st.cache_data.clear,
    )
    st.sidebar.caption("OpenF1 · análise local")

    if navigation == "Resumo":
        st.subheader("Resumo executivo")
        render_data_table(
            state["session_summaries"],
            "Panorama de temporadas, circuitos, vencedores e melhores voltas",
        )
    elif navigation == "Sessões":
        render_sessions_section(state)
    elif navigation == "Pilotos":
        render_drivers_section(state)
    elif navigation == "Voltas":
        render_laps_section(state)
    else:
        render_raw_section(state)


if __name__ == "__main__":
    main()
