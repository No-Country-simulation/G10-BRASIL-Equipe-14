import re
import json
from datetime import datetime

import streamlit as st
from src.ui import SOURCE_LABELS, badges, metric_card, page_header

from src.config import (
    FEELINGS_ENUM,
    STATUSES_ENUM,
    TARGETS_ENUM,
    ENGAGEMENT_BADGES,
    PACKAGE_STATUS_BADGES,
    REVIEW_BADGES,
)
from src.services.output_packages import list_output_packages


def load_suggested_content() -> list[dict]:
    packages = list_output_packages()
    for package in packages:
        for index, content in enumerate(package["suggested_content"]):
            content["id"] = f"{package['package_id']}_{index}"
            content["review_status"] = "pending"
    return packages


def set_review(content: dict, status: str) -> None:
    content["review_status"] = status


def format_period(reference_period: str) -> str:
    start, end = (datetime.fromisoformat(part) for part in reference_period.split("/"))
    return f"{start:%d/%m/%Y} → {end:%d/%m/%Y}"


def render_package_header(package: dict) -> None:
    with st.container(border=True):
        st.caption("Lote")
        st.subheader(package["linked_batch_id"], anchor=False)
        badges([PACKAGE_STATUS_BADGES[package["status"]][0], package["package_id"]], states=[{"success": "success", "suspended": "warning", "error": "error"}.get(package["status"])])


def render_reference_period(package: dict) -> None:
    st.markdown(f"**Período de referência:** {format_period(package['reference_period'])}")


def render_feeling_card(feeling: str) -> None:
    metric_card("Sentimento predominante", FEELINGS_ENUM[feeling], "Avaliação do pacote demonstrativo")


def render_processing_summary(package: dict) -> None:
    summary = package["processing_summary"]
    st.subheader("Resumo do processamento", anchor=False)
    col1, col2 = st.columns(2)
    with col1:
        metric_card("Interações processadas", summary["total_interactions"], "No pacote selecionado")
    with col2:
        render_feeling_card(summary["predominant_feeling"])
    st.markdown("**Interações por origem**")
    breakdown = summary["sources_breakdown"]
    for col, (source, count) in zip(st.columns(max(1, len(breakdown))), breakdown.items()):
        with col:
            metric_card(SOURCE_LABELS.get(source, source), count, f"{count / max(1, summary['total_interactions']):.0%} do total")
    st.markdown("**Principais tópicos**")
    badges(summary["main_topics"])


def render_content_badges(content: dict) -> None:
    labels = [TARGETS_ENUM[content["target"]], ENGAGEMENT_BADGES[content["potential_engagement"]][0]]
    if content["review_status"] in REVIEW_BADGES:
        labels.append(REVIEW_BADGES[content["review_status"]][0])
    badges(labels, states=[None, None, {"approved": "success", "rejected": "error"}.get(content["review_status"])])


def render_pending_content(content: dict) -> None:
    with st.container(border=True):
        render_content_badges(content)
        content["body"] = st.text_area(content["title"], content["body"], key=f"body_{content['id']}", height=160)
        with st.container(horizontal=True, gap="xsmall"):
            st.button("Aprovar", type="primary", key=f"ok_{content['id']}", on_click=set_review, args=(content, "approved"))
            st.button(
                "Rejeitar",
                key=f"no_{content['id']}",
                on_click=set_review, args=(content, "rejected"),
            )


def split_body(body: str) -> tuple[str, str]:
    tags = " ".join(re.findall(r"(?<!\S)#\w+", body))
    text = re.sub(r"(?<!\S)#\w+", "", body)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip(), tags


def render_copyable_parts(content: dict) -> None:
    text, tags = split_body(content["body"])
    parts = [("Título", content["title"]), ("Texto", text), ("Etiquetas", tags)]
    for label, value in parts:
        if value:
            st.caption(label)
            st.code(value, language=None, wrap_lines=True)


def render_reviewed_content(content: dict) -> None:
    with st.container(border=True):
        render_content_badges(content)
        if content["review_status"] == "approved":
            render_copyable_parts(content)
        else:
            st.markdown(f"**{content['title']}**")
            st.write(content["body"])
        st.button(
            "Refazer revisão",
            key=f"undo_{content['id']}",
            on_click=set_review, args=(content, "pending"),
        )


def render_suggested_content(package: dict) -> None:
    contents = package["suggested_content"]
    st.subheader("Conteúdos sugeridos", anchor=False)
    counts = {status: sum(c["review_status"] == status for c in contents) for status in STATUSES_ENUM}
    status = st.radio(
        "Status da revisão", list(STATUSES_ENUM), horizontal=True,
        key=f"curation_status_{package['package_id']}",
        format_func=lambda s: f"{STATUSES_ENUM[s]} ({counts[s]})",
    )
    shown = [c for c in contents if c["review_status"] == status]
    if not shown:
        empty_labels = {"pending": "pendente", "approved": "aprovado", "rejected": "rejeitado"}
        st.info(f"Nenhum conteúdo {empty_labels[status]} neste pacote.")
        return
    render = render_pending_content if status == "pending" else render_reviewed_content
    for content in shown:
        render(content)

def render_curation() -> None:
    page_header("Curadoria editorial", "Revise, ajuste e aprove conteúdos sugeridos antes de preparar sua distribuição.", "Operação / Revisão humana")
    st.info("Demonstração: os pacotes são exemplos. Alterações e aprovações ficam apenas nesta sessão e não publicam nem persistem conteúdo na nuvem.")
    if "packages" not in st.session_state:
        st.session_state["packages"] = load_suggested_content()
    packages = {p["linked_batch_id"]: p for p in st.session_state["packages"]}
    if not packages:
        st.info("Nenhum pacote disponível para curadoria.")
        return
    request = st.session_state.get("nav_request", {})
    requested_batch = request.get("batch")
    default_batch = requested_batch if requested_batch in packages else next(iter(packages))
    batch_id = st.selectbox(
        "Selecione o lote", list(packages),
        index=list(packages).index(default_batch),
        key=f"curation_batch_{request.get('nonce', 0)}",
    )
    package = packages[batch_id]
    contents = package["suggested_content"]
    for col, (status, label) in zip(st.columns(3), STATUSES_ENUM.items()):
        with col:
            metric_card(label, sum(c["review_status"] == status for c in contents), "Conteúdos do lote selecionado")
    approved = [dict(c) for c in contents if c["review_status"] == "approved"]
    if approved:
        st.download_button("Exportar conteúdos aprovados", json.dumps(approved, ensure_ascii=False, indent=2), f"{package['package_id']}-aprovados.json", "application/json")

    render_package_header(package)
    render_processing_summary(package)
    render_reference_period(package)
    render_suggested_content(package)


render_curation()
