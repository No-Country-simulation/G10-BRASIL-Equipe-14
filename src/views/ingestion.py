from typing import Any

import requests
import streamlit as st

from src.config import INGESTION_TEXT_AREA_NAME
from src.services.ingestion import parse_input, parse_pasted_text, send_to_ingestion


def collect_items(files: list, text: str) -> tuple[list[tuple[str, Any]], list[str]]:
    items: list[tuple[str, Any]] = []
    errors: list[str] = []
    sources = [(f.name, lambda f=f: parse_input(f.getvalue(), f.name.lower().endswith(".csv"))) for f in files or []]
    if text.strip():
        sources.append((INGESTION_TEXT_AREA_NAME, lambda: parse_pasted_text(text)))
    for name, parse in sources:
        try:
            items.append((name, parse()))
        except ValueError as exc:
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


def render_ingestion() -> None:
    st.header("Ingestão de dados")

    with st.form("ingestion_form"):
        files = st.file_uploader("Adicione os arquivos JSON ou CSV", type=["json", "csv"], accept_multiple_files=True)
        text = st.text_area(
            "Ou cole os dados no formato JSON ou CSV",
            height=250,
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
        with st.expander("Ver detalhes"):
            for error in errors:
                st.markdown(f"- {error}")
        return

    if previewed:
        render_preview(items)
        return

    with st.spinner("Enviando..."):
        for name, data in items:
            try:
                status = send_to_ingestion(data)
            except requests.RequestException as exc:
                st.error(f"{name}: falha ao enviar o arquivo.")
                with st.expander("Ver detalhes"):
                    st.code(str(exc))
                continue
            if requests.codes.ok <= status < requests.codes.multiple_choices:
                st.success(f"{name}: enviado.")
            else:
                st.error(f"{name}: falha no envio.")
                with st.expander("Ver detalhes"):
                    st.markdown(f"Status HTTP: `{status}`")


render_ingestion()
