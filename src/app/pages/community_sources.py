import time
from collections.abc import Callable

import streamlit as st
import streamlit_shadcn_ui as ui

from config import PROCESSING_SECONDS

COMMUNITY_SOURCES_INPUTS_SAMPLE = [
    {
        "id": "lote-se-001",
        "source_key": "stackoverflow",
        "source": "Stack Exchange",
        "url": "https://stackoverflow.com/questions/tagged/duckdb",
        "period": ("2026-10-13", "2026-10-20"),
        "interactions": 128,
        "authors": 94,
        "with_content": 121,
        "avg_score": 3.4,
        "top_tags": [("duckdb", 52), ("python", 41), ("json-schema", 18), ("pandas", 15), ("sql", 12)],
    },
    {
        "id": "lote-ma-002",
        "source_key": "mastodon",
        "source": "Mastodon",
        "url": "https://mastodon.social/tags/opensource",
        "period": ("2026-10-13", "2026-10-20"),
        "interactions": 342,
        "authors": 207,
        "with_content": 342,
        "avg_score": 7.9,
        "top_tags": [("opensource", 120), ("python", 64), ("llm", 58), ("devops", 33), ("observability", 21)],
    },
    {
        "id": "lote-hn-003",
        "source_key": "hackernews",
        "source": "Hacker News",
        "url": "https://news.ycombinator.com/",
        "period": ("2026-10-13", "2026-10-20"),
        "interactions": 76,
        "authors": 61,
        "with_content": 49,
        "avg_score": 112.6,
        "top_tags": [("show_hn", 24), ("story", 76), ("ai", 19), ("rust", 11)],
    },
    {
        "id": "lote-se-004",
        "source_key": "stackoverflow",
        "source": "Stack Exchange",
        "url": "https://stackoverflow.com/questions/tagged/n8n",
        "period": ("2026-10-06", "2026-10-13"),
        "interactions": 87,
        "authors": 70,
        "with_content": 84,
        "avg_score": 2.1,
        "top_tags": [("n8n", 44), ("docker", 29), ("webhook", 17), ("automation", 14)],
    },
]


def get_community_source(batch_id: str) -> dict:
    return next(b for b in COMMUNITY_SOURCES_INPUTS_SAMPLE if b["id"] == batch_id)


def go_to_curation(batch_id: str) -> None:
    nonce = st.session_state.get("nav_request", {}).get("nonce", 0) + 1
    st.session_state["nav_request"] = {"batch": batch_id, "nonce": nonce}
    st.switch_page("pages/curation.py")


def render_community_source_card(batch: dict, on_open_curation: Callable[[str], None]) -> None:
    start, end = batch["period"]
    with st.container(border=True):
        ui.badges([(batch["source"], "default"), (batch["id"], "outline")], key=f"head_{batch['id']}")
        st.caption(f"Período de referência: {start} → {end}")

        figures = [
            ("Interações", batch["interactions"]),
            ("Autores únicos", batch["authors"]),
            ("Com conteúdo", batch["with_content"]),
            ("Score médio", f"{batch['avg_score']:.1f}"),
        ]
        for col, (label, value) in zip(st.columns(len(figures)), figures):
            with col:
                ui.metric_card(label=label, value=str(value), key=f"s_{batch['id']}_{label}")

        st.markdown("**Principais tags**")
        ui.badges([(f"{tag} ({n})", "secondary") for tag, n in batch["top_tags"]], key=f"tags_{batch['id']}")
        processed = st.session_state.setdefault("processed_batches", set())
        with st.container(horizontal=True, gap="xsmall"):
            st.link_button("Abrir fonte", batch["url"])
            started = st.button("Iniciar processamento", key=f"process_{batch['id']}")
            open_curation = batch["id"] in processed and st.button(
                "Ver na Curadoria", key=f"curation_{batch['id']}"
            )
        if started:
            with st.spinner("Processando lote..."):
                time.sleep(PROCESSING_SECONDS)
            processed.add(batch["id"])
            st.toast("Processamento concluído.", icon=":material/check_circle:")
            st.rerun()
        if open_curation:
            on_open_curation(batch["id"])


def render_community_sources_page(on_open_curation: Callable[[str], None]) -> None:
    st.header("Fontes da comunidade")

    sources = sorted({b["source"] for b in COMMUNITY_SOURCES_INPUTS_SAMPLE})
    selected = st.multiselect("Fontes", sources, default=sources)
    shown = [b for b in COMMUNITY_SOURCES_INPUTS_SAMPLE if b["source"] in selected]

    col1, col2 = st.columns(2)
    with col1:
        ui.metric_card(label="Lotes", value=str(len(shown)), key="in_records")
    with col2:
        ui.metric_card(label="Interações", value=str(sum(b["interactions"] for b in shown)), key="in_interactions")

    if not shown:
        st.info("Nenhum lote para as fontes selecionadas.")
    for batch in shown:
        render_community_source_card(batch, on_open_curation)


def render_sources() -> None:
    render_community_sources_page(go_to_curation)


render_sources()
