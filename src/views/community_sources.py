import time
from collections.abc import Callable

import streamlit as st
import streamlit_shadcn_ui as ui

from config import PROCESSING_SECONDS
from src.services.community_sources import list_community_sources

def go_to_curation(batch_id: str) -> None:
    nonce = st.session_state.get("nav_request", {}).get("nonce", 0) + 1
    st.session_state["nav_request"] = {"batch": batch_id, "nonce": nonce}
    st.switch_page("views/curation.py")


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

    batches = list_community_sources()
    sources = sorted({b["source"] for b in batches})
    selected = st.multiselect("Fontes", sources, default=sources)
    shown = [b for b in batches if b["source"] in selected]

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
