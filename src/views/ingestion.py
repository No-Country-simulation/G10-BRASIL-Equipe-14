import logging
from typing import Any

import requests
import streamlit as st

from src.config import INGESTION_TEXT_AREA_NAME, MAX_UPLOAD_FILE_SIZE_BYTES, MAX_UPLOAD_FILE_SIZE_MB
from src.services.ingestion import parse_input, parse_pasted_text, send_to_ingestion

logger = logging.getLogger(__name__)


def collect_items(files: list, text: str) -> tuple[list[tuple[str, Any]], list[str]]:
    items: list[tuple[str, Any]] = []
    errors: list[str] = []
    sources = []
    for f in files or []:
        if f.size > MAX_UPLOAD_FILE_SIZE_BYTES:
            errors.append(f"**{f.name}**: arquivo excede o limite de {MAX_UPLOAD_FILE_SIZE_MB} MB.")
            continue
        sources.append((f.name, lambda f=f: parse_input(f.getvalue(), f.name.lower().endswith(".csv"))))
    if text.strip():
        sources.append((INGESTION_TEXT_AREA_NAME, lambda: parse_pasted_text(text)))
    for name, parse in sources:
        try:
            items.append((name, parse()))
        except ValueError as exc:
            logger.warning("Invalid ingestion input %r: %s", name, exc)
            errors.append(f"**{name}**: {exc}")
    return items, errors


def render_preview(items: list[tuple[str, Any]]) -> None:
    for name, data in items:
        records = [data] if isinstance(data, dict) else data
        is_table = bool(records) and isinstance(records, list) and all(isinstance(r, dict) for r in records)
        count = len(records) if isinstance(records, list) else 1
        with st.expander(f"{name} — {count} registro(s)", expanded=True):
            if is_table:
                st.dataframe(records, width="stretch")
            else:
                st.json(data)


def send_items(items: list[tuple[str, Any]]) -> None:
    with st.spinner("Enviando..."):
        for name, data in items:
            try:
                status = send_to_ingestion(data)
            except requests.RequestException:
                logger.exception("Ingestion service unavailable while sending %r", name)
                st.error(f"{name}: serviço de ingestão indisponível. Tente novamente em instantes.")
                continue
            if requests.codes.ok <= status < requests.codes.multiple_choices:
                st.success(f"{name}: enviado.")
            else:
                logger.error("Ingestion failed for %r: HTTP %s", name, status)
                st.error(f"{name}: falha no envio.")


@st.dialog("Confirmar envio")
def confirm_send(items: list[tuple[str, Any]]) -> None:
    total = sum(len(data) if isinstance(data, list) else 1 for _, data in items)
    st.write(f"Enviar **{len(items)}** item(ns) com **{total}** registro(s) para a ingestão?")
    for name, _ in items:
        st.markdown(f"- {name}")
    actions = st.empty()
    with actions.container(horizontal=True):
        confirmed = st.button("Confirmar envio", type="primary", key="ingestion_confirm")
        cancelled = st.button("Cancelar", key="ingestion_cancel")
    if cancelled:
        st.rerun()
    if confirmed:
        actions.empty()
        send_items(items)


def render_ingestion() -> None:
    st.header("Ingestão de dados")

    with st.form("ingestion_form"):
        files = st.file_uploader(
            "Adicione os arquivos JSON ou CSV",
            type=["json", "csv"],
            accept_multiple_files=True,
            help=f"Tamanho máximo por arquivo: {MAX_UPLOAD_FILE_SIZE_MB} MB.",
        )
        text = st.text_area(
            "Ou cole os dados no formato JSON ou CSV",
            height=250,
            help=(
                "Cole um objeto ou lista JSON, ou um CSV com cabeçalho na primeira linha "
                "(separadores aceitos: vírgula, ponto e vírgula, tab ou barra vertical). "
                "Se também enviar arquivos, o texto colado é tratado como mais um item."
            ),
            placeholder='{"source": "..."}  ou  id,source,url',
        )
        preview_col, send_col = st.columns(2)
        previewed = preview_col.form_submit_button("Pré-visualizar", width="stretch")
        submitted = send_col.form_submit_button("Validar e enviar", type="primary", width="stretch")

    if not (previewed or submitted):
        return

    items, errors = collect_items(files, text)
    if not items and not errors:
        st.warning("Envie ao menos um arquivo ou cole um JSON/CSV.")
        return
    if errors:
        if len(errors) == 1:
            st.error("JSON ou CSV inválido.")
        else:
            st.error(f"{len(errors)} JSON ou CSV inválidos.")
        return

    if previewed:
        render_preview(items)
        return

    confirm_send(items)


render_ingestion()
