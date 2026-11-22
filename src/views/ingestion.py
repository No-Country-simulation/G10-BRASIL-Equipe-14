import hashlib
import logging
from typing import Any

import requests
import streamlit as st
from src.ui import page_header, badges

from src.config import (
    INGESTION_TEXT_AREA_NAME,
    MAX_UPLOAD_FILE_COUNT,
    MAX_TOTAL_UPLOAD_SIZE_BYTES,
    MAX_TOTAL_UPLOAD_SIZE_MB,
    MAX_UPLOAD_FILE_SIZE_BYTES,
    MAX_UPLOAD_FILE_SIZE_MB,
)
from src.services.ingestion import parse_input, parse_pasted_text_with_format, send_to_ingestion, validate_input
from src.services.faq_drafts import generate_faq_from_triage
from src.services.raw_ingestion import SOURCES, prepare_upload, trigger_triage, upload_raw
from src.services.recurrence_drafts import generate_recurrence_from_triage
from src.services.success_case_drafts import generate_success_case_from_triage
from src.services.bucket_download import BucketDownloadError, download_folder

logger = logging.getLogger(__name__)

SENT_SIGNATURE_KEY = "ingestion_sent_signature"
PREVIEW_KEY = "ingestion_preview"


def _validate(data: list[dict[str, Any]], as_csv: bool) -> list[dict[str, Any]]:
    data, schema_errors = validate_input(data, as_csv)
    if schema_errors:
        raise ValueError("fora do schema de entrada:\n" +
                         "\n".join(f"- {e}" for e in schema_errors))
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
    if files and len(files) > MAX_UPLOAD_FILE_COUNT:
        return items, [f"Envie no máximo {MAX_UPLOAD_FILE_COUNT} arquivos por vez (recebidos: {len(files)})."]
    total_size = sum(f.size for f in files or [])
    if total_size > MAX_TOTAL_UPLOAD_SIZE_BYTES:
        return items, [f"O tamanho total dos arquivos excede o limite de {MAX_TOTAL_UPLOAD_SIZE_MB} MB."]
    sources = []
    for f in files or []:
        if f.size > MAX_UPLOAD_FILE_SIZE_BYTES:
            errors.append(
                f"**{f.name}**: arquivo excede o limite de {MAX_UPLOAD_FILE_SIZE_MB} MB.")
            continue
        sources.append((f.name, lambda f=f: _parse_and_validate(
            f.getvalue(), f.name.lower().endswith(".csv"))))
    if text.strip():
        sources.append((INGESTION_TEXT_AREA_NAME, lambda: _validate(
            *parse_pasted_text_with_format(text))))
    for name, parse in sources:
        try:
            items.append((name, parse()))
        except ValueError as exc:
            logger.warning("Invalid ingestion input %r: %s", name, exc)
            errors.append(f"**{name}**: {exc}")
    return items, errors


def render_preview(items: list[tuple[str, list[dict[str, Any]]]]) -> None:
    for name, records in items:
        count_label = "registro" if len(records) == 1 else "registros"
        with st.expander(f"{name} — {len(records)} {count_label}", expanded=True):
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
                label = name if len(
                    payloads) == 1 else f"{name}, registro {index}"
                try:
                    response = send_to_ingestion(payload)
                except requests.RequestException:
                    logger.exception(
                        "Ingestion service unavailable while sending %r", label)
                    failed += 1
                    st.error(f"{label}: falha de comunicação com o serviço.")
                    continue
                status = response.status_code
                if requests.codes.ok <= status < requests.codes.multiple_choices:
                    sent += 1
                    st.success(f"{label}: enviado.")
                else:
                    logger.error(
                        "Ingestion failed for %r: HTTP %s: %.500s", label, status, response.text)
                    failed += 1
                    st.error(f"{label}: falha no envio.")
                    st.caption(f"Status HTTP recebido: {status}")
    return sent, failed


def render_send_summary(sent: int, failed: int) -> None:
    total = sent + failed
    if failed == 0:
        st.success(f"Registros enviados com sucesso: {sent} de {total}.")
    elif sent == 0:
        st.error(
            f"Nenhum registro foi enviado. Falhas no envio: {failed} de {total}.")
    else:
        st.warning(
            f"Envio parcial: {sent} de {total} registros enviados com sucesso. Falhas no envio: {failed}.")


@st.dialog("Confirmar envio")
def confirm_send(items: list[tuple[str, list[dict[str, Any]]]], signature: str) -> None:
    total = sum(len(records) for _, records in items)
    item_label = "entrada" if len(items) == 1 else "entradas"
    record_label = "registro" if total == 1 else "registros"
    st.write(
        f"Enviar **{len(items)}** {item_label} com **{total}** {record_label} para a ingestão?")
    with st.expander("Ver fontes"):
        for name, records in items:
            label = "registro" if len(records) == 1 else "registros"
            st.markdown(f"- {name} — {len(records)} {label}")
    actions = st.empty()
    with actions.container(horizontal=True):
        confirmed = st.button(
            "Confirmar envio", type="primary", key="ingestion_confirm")
        cancelled = st.button("Cancelar", key="ingestion_cancel")
    if cancelled:
        st.rerun()
    if confirmed:
        actions.empty()
        sent, failed = send_items(items)
        render_send_summary(sent, failed)
        if not failed:
            st.session_state[SENT_SIGNATURE_KEY] = signature


def render_errors(errors: list[str]) -> None:
    st.error("Não foi possível validar a entrada.")
    with st.expander("Ver detalhes", expanded=True):
        for error in errors:
            st.markdown(f"- {error}")


def render_ingestion() -> None:
    page_header("Ingestão de dados", "Prepare a entrada de interações para transformar conversas em ativos de conhecimento.",
                "Operação / Entrada de dados")
    with st.expander("Orientações de preenchimento", expanded=True):
        st.write(
            "Selecione a fonte, informe o tema e anexe um JSON bruto no formato "
            "do workflow escolhido. O upload grava o arquivo na OCI e inicia a triagem."
        )
        st.caption(
            "Para Hacker News, use o JSON consolidado do WF07, com publicações e comentários.")
    with st.container(border=True):
        folder = st.selectbox("pastas disponíveis", [
                              "raw/", "processed/"], key="download_folder")
        if st.button("Download", key="request_bucket_download"):
            st.session_state.pop("bucket_download", None)
            try:
                with st.spinner("Preparando os arquivos para download..."):
                    content = download_folder(folder)
                st.session_state["bucket_download"] = {
                    "folder": folder, "content": content}
            except BucketDownloadError as exc:
                status = exc.response.status_code if exc.response is not None else None
                logger.error(
                    "Falha ao baixar a pasta %s pelo WF05 (tipo=%s, status_http=%s)",
                    folder,
                    type(exc.__cause__ or exc).__name__,
                    status,
                )
                st.error(
                    "Não foi possível baixar os arquivos. Confira a conexão e a configuração do WF05.")
            except ValueError as exc:
                st.error(str(exc))
        archive = st.session_state.get("bucket_download")
        if archive and archive["folder"] == folder:
            st.download_button(
                "Salvar ZIP", data=archive["content"],
                file_name=f"{folder.rstrip('/')}_results.zip", mime="application/zip",
                on_click="ignore",
            )
        st.caption(
            "Salve o ZIP, extraia os arquivos e selecione o JSON desejado abaixo. O local de download depende do navegador.")

    source = st.selectbox("Fonte dos dados", tuple(SOURCES), index=None)
    tag = st.text_input(
        "Tema", placeholder="artificial-intelligence", max_chars=80)
    limit = st.number_input("Limite de itens para triagem",
                            min_value=1, value=1, step=1)
    file = st.file_uploader(
        "Arquivo JSON bruto", type=["json"], help=f"Até {MAX_UPLOAD_FILE_SIZE_MB} MB."
    )
    if not source or not tag or file is None:
        return
    try:
        workflow_tag, key, content, count = prepare_upload(
            source, tag, file.getvalue())
    except ValueError as exc:
        st.error(str(exc))
        return

    st.caption(f"{count} registro(s) no arquivo. Objeto OCI: `{key}`")
    saved = st.session_state.setdefault("raw_ingestion_saved", set())
    completed = st.session_state.setdefault("raw_ingestion_completed", {})
    run_key = (key, limit)
    if run_key in completed:
        show_triage_result(completed[run_key])
        return
    if not st.button("Tentar triagem novamente" if key in saved else "Upload", type="primary"):
        return

    with st.spinner("Gravando o arquivo e aguardando a triagem..."):
        try:
            if key not in saved:
                upload_raw(key, content)
                saved.add(key)
            result = trigger_triage(source, workflow_tag, limit)
        except requests.RequestException:
            st.error(
                "Falha de comunicação. A operação remota pode ter sido iniciada. Confira antes de repetir.")
            if key in saved:
                st.info("O arquivo já está gravado na OCI.")
            return
        except ValueError as exc:
            st.error(str(exc))
            if key in saved:
                st.info("O arquivo já está gravado na OCI.")
            return
        completed[run_key] = result
        show_triage_result(result)


def show_triage_result(result: dict) -> None:
    st.success("Arquivo gravado na OCI e triagem concluída.")
    if result.get("execution_id"):
        st.write(f"Execução n8n: `{result['execution_id']}`")
    if result.get("count") is not None:
        st.write(f"Itens processados: {result['count']}")
    try:
        package = (
            generate_faq_from_triage(result)
            or generate_success_case_from_triage(result)
            or generate_recurrence_from_triage(result)
        )
    except (KeyError, OSError, TypeError, ValueError):
        logger.warning("Falha ao preparar o pacote da execução %s",
                       result.get("execution_id"))
        st.error("A triagem concluiu, mas não foi possível preparar os rascunhos.")
        st.button("Tentar geração novamente")
        return
    if package:
        st.success(
            f"Rascunhos disponíveis na Curadoria, no lote `{package.stem}`.")


render_ingestion()
