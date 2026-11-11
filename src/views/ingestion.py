import hashlib
import logging
from typing import Any

import requests
import streamlit as st

from src.config import INGESTION_TEXT_AREA_NAME, MAX_UPLOAD_FILE_SIZE_BYTES, MAX_UPLOAD_FILE_SIZE_MB
from src.services.ingestion import parse_input, parse_pasted_text_with_format, send_to_ingestion, validate_input

logger = logging.getLogger(__name__)

SENT_SIGNATURE_KEY = "ingestion_sent_signature"


def _validate(data: list[dict[str, Any]], as_csv: bool) -> list[dict[str, Any]]:
    data, schema_errors = validate_input(data, as_csv)
    if schema_errors:
        raise ValueError("fora do schema de entrada:\n" + "\n".join(f"- {e}" for e in schema_errors))
    return data


def _parse_and_validate(raw: bytes, as_csv: bool) -> list[dict[str, Any]]:
    return _validate(parse_input(raw, as_csv), as_csv)


def input_signature(files: list, text: str) -> str:
    digest = hashlib.sha256()
    for f in files or []:
        digest.update(f.name.encode() + b"\0" + f.getvalue() + b"\0")
    digest.update(text.strip().encode())
    return digest.hexdigest()


def collect_items(files: list, text: str) -> tuple[list[tuple[str, list[dict[str, Any]]]], list[str]]:
    items: list[tuple[str, list[dict[str, Any]]]] = []
    errors: list[str] = []
    sources = []
    for f in files or []:
        if f.size > MAX_UPLOAD_FILE_SIZE_BYTES:
            errors.append(f"**{f.name}**: arquivo excede o limite de {MAX_UPLOAD_FILE_SIZE_MB} MB.")
            continue
        sources.append((f.name, lambda f=f: _parse_and_validate(f.getvalue(), f.name.lower().endswith(".csv"))))
    if text.strip():
        sources.append((INGESTION_TEXT_AREA_NAME, lambda: _validate(*parse_pasted_text_with_format(text))))
    for name, parse in sources:
        try:
            items.append((name, parse()))
        except ValueError as exc:
            logger.warning("Invalid ingestion input %r: %s", name, exc)
            errors.append(f"**{name}**: {exc}")
    return items, errors


def render_preview(items: list[tuple[str, list[dict[str, Any]]]]) -> None:
    for name, records in items:
        with st.expander(f"{name} — {len(records)} registro(s)", expanded=True):
            if len(records) == 1:
                st.json(records[0])
            else:
                st.dataframe(records, width="stretch")


def send_items(items: list[tuple[str, list[dict[str, Any]]]]) -> tuple[int, int]:
    sent = 0
    failed = 0
    with st.spinner("Enviando..."):
        for name, payloads in items:
            for index, payload in enumerate(payloads, start=1):
                label = name if len(payloads) == 1 else f"{name}, registro {index}"
                try:
                    response = send_to_ingestion(payload)
                except requests.RequestException:
                    logger.exception("Ingestion service unavailable while sending %r", label)
                    failed += 1
                    st.error(f"{label}: falha de comunicação com o serviço.")
                    continue
                status = response.status_code
                if requests.codes.ok <= status < requests.codes.multiple_choices:
                    sent += 1
                    st.success(f"{label}: enviado.")
                else:
                    logger.error("Ingestion failed for %r: HTTP %s: %.500s", label, status, response.text)
                    failed += 1
                    st.error(f"{label}: falha no envio.")
                    st.caption(f"Status HTTP recebido: {status}")
    return sent, failed


def render_send_summary(sent: int, failed: int) -> None:
    total = sent + failed
    if failed == 0:
        st.success(f"{sent} de {total} registro(s) enviado(s) com sucesso.")
    elif sent == 0:
        st.error(f"Nenhum registro foi enviado: {failed} de {total} falhou(aram).")
    else:
        st.warning(f"Envio parcial: {sent} de {total} registro(s) enviado(s) com sucesso, {failed} falhou(aram).")


@st.dialog("Confirmar envio")
def confirm_send(items: list[tuple[str, list[dict[str, Any]]]], signature: str) -> None:
    total = sum(len(records) for _, records in items)
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
        sent, failed = send_items(items)
        render_send_summary(sent, failed)
        if not failed:
            st.session_state[SENT_SIGNATURE_KEY] = signature


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
            placeholder='{"id": "...", "source": "..."}  ou  id,source,url',
        )
        preview_col, send_col = st.columns(2)
        previewed = preview_col.form_submit_button("Pré-visualizar", width="stretch")
        already_sent = st.session_state.get(SENT_SIGNATURE_KEY) == input_signature(files, text)
        submitted = send_col.form_submit_button(
            "✓ Enviado — altere a entrada para reenviar" if already_sent else "Validar e enviar",
            type="primary",
            width="stretch",
            disabled=already_sent,
        )

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
        with st.expander("Ver detalhes", expanded=True):
            for error in errors:
                st.markdown(f"- {error}")
        return

    if previewed:
        render_preview(items)
        return

    confirm_send(items, input_signature(files, text))


render_ingestion()
