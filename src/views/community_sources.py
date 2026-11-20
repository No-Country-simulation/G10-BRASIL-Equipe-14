import time
from datetime import date
from collections.abc import Callable

import streamlit as st
from src.ui import badges, metric_card, page_header

from src.config import PROCESSING_SECONDS
from src.services.community_sources import list_community_sources

def go_to_curation(batch_id: str) -> None:
    nonce = st.session_state.get("nav_request", {}).get("nonce", 0) + 1
    st.session_state["nav_request"] = {"batch": batch_id, "nonce": nonce}
    st.switch_page("views/curation.py")


def render_community_source_card(batch: dict, on_open_curation: Callable[[str], None]) -> None:
    start, end = batch["period"]
    with st.container(border=True):
        badges([batch["source"], batch["id"], "Demonstração"])
        st.caption(f"Período de referência: {date.fromisoformat(start):%d/%m/%Y} → {date.fromisoformat(end):%d/%m/%Y}")

        figures = [
            ("Interações", batch["interactions"], "Neste lote"),
            ("Autores únicos", batch["authors"], "Neste lote"),
            ("Interações com conteúdo", batch["with_content"], "Neste lote"),
            ("Pontuação média", f"{batch['avg_score']:.1f}".replace(".", ","), "Pontuação da plataforma de origem"),
        ]
        for col, (label, value, note) in zip(st.columns(len(figures)), figures):
            with col:
                metric_card(label, value, note)

        st.markdown("**Principais etiquetas**")
        badges([f"{tag} ({n})" for tag, n in batch["top_tags"]])
        if "processed_batches" not in st.session_state:
            st.session_state["processed_batches"] = set()
        processed = st.session_state["processed_batches"]
        with st.container(horizontal=True, gap="xsmall"):
            st.link_button("Abrir fonte", batch["url"])
            started = st.button("Simular processamento", key=f"process_{batch['id']}", type="primary")
            open_curation = batch["id"] in processed and st.button(
                "Abrir curadoria", key=f"curation_{batch['id']}"
            )
        if started:
            with st.spinner("Processando lote..."):
                time.sleep(PROCESSING_SECONDS)
            st.session_state["processed_batches"] = processed | {batch["id"]}
            st.toast("Simulação concluída nesta sessão.", icon=":material/check_circle:")
            st.rerun()
        if open_curation:
            on_open_curation(batch["id"])


def render_community_sources_page(on_open_curation: Callable[[str], None]) -> None:
    page_header("Fontes da comunidade", "Explore a origem das conversas e os lotes disponíveis para o fluxo editorial.", "Operação / Monitoramento")
    st.info("Ambiente demonstrativo: os lotes abaixo são exemplos. O processamento é simulado e não executa a coleta nas fontes.")

    batches = list_community_sources()
    sources = sorted({b["source"] for b in batches})
    selected = st.multiselect("Fontes", sources, default=sources, placeholder="Selecione as fontes")
    shown = [b for b in batches if b["source"] in selected]

    col1, col2 = st.columns(2)
    with col1:
        metric_card("Lotes disponíveis", len(shown), "No recorte selecionado · Demonstração")
    with col2:
        metric_card("Interações", sum(b["interactions"] for b in shown), "Soma dos lotes selecionados · Demonstração")

    if not shown:
        st.info("Nenhum lote para as fontes selecionadas.")
    for batch in shown:
        render_community_source_card(batch, on_open_curation)


def render_sources() -> None:
    render_community_sources_page(go_to_curation)


render_sources()
