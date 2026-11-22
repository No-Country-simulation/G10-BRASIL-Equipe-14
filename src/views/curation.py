from datetime import datetime

import streamlit as st
from requests import RequestException
import streamlit_shadcn_ui as ui

from src.config import (
    FEELINGS_COLORS_ENUM,
    FEELINGS_ENUM,
    STATUSES_ENUM,
    TARGETS_ENUM,
    ENGAGEMENT_BADGES,
    PACKAGE_STATUS_BADGES,
    REVIEW_BADGES,
)
from src.services.approved_packages import can_publish, publish_approved_package
from src.services.faq_drafts import load_draft_packages, save_draft_review
from src.services.output_packages import list_output_packages
from src.services.curation_store import export_approved, load_reviews, save_review
from src.utils.regex_patterns import (
    EXTRA_NEWLINES_RE,
    HASHTAG_TOKEN_RE,
    HORIZONTAL_SPACING_RE,
)


def load_suggested_content() -> list[dict]:
    packages = list_output_packages()
    saved = load_reviews()
    for package in packages:
        for index, content in enumerate(package["suggested_content"]):
            content["id"] = f"{package['package_id']}_{index}"
            content["package_id"] = package["package_id"]
            content["batch_id"] = package["linked_batch_id"]
            content["review_status"] = "pending"
            if content["id"] in saved:
                content["review_status"] = saved[content["id"]]["review_status"]
                content["body"] = saved[content["id"]]["body"]
    return packages


def set_review(content: dict, status: str) -> None:
    body = st.session_state.get(f"body_{content['id']}", content["body"])
    if content["id"].startswith(("wf09-", "wf10-", "wf11-")):
        try:
            save_draft_review(content, status, body)
        except OSError:
            st.error("Não foi possível salvar a decisão de curadoria.")
            return
        return
    edited = st.session_state.get(f"body_{content['id']}")
    if edited is not None:
        content["body"] = edited
    content["review_status"] = status
    save_review(content)


def format_period(reference_period: str) -> str:
    start, end = (datetime.fromisoformat(part)
                  for part in reference_period.split("/"))
    return f"{start:%d/%m/%Y} → {end:%d/%m/%Y}"


def render_package_header(package: dict) -> None:
    with st.container(border=True):
        st.caption("Lote")
        st.title(package["linked_batch_id"], anchor=False)
        ui.badges(
            [PACKAGE_STATUS_BADGES[package["status"]],
                (package["package_id"], "outline")],
            key=f"pkg_status_{package['package_id']}",
        )


def render_reference_period(package: dict) -> None:
    st.markdown(
        f"**Período de referência:** {format_period(package['reference_period'])}")


def render_feeling_card(feeling: str) -> None:
    background, border = FEELINGS_COLORS_ENUM[feeling]
    st.markdown(
        f"""
        <div style="background:{background}; border:1px solid {border}; border-radius:12px; padding:16px 20px;">
            <div style="color:#4b5563; font-size:0.875rem;">Sentimento predominante</div>
            <div style="color:#111827; font-size:1.5rem; font-weight:700; margin-top:4px;">
                {FEELINGS_ENUM[feeling]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_processing_summary(package: dict) -> None:
    summary = package["processing_summary"]
    pid = package["package_id"]
    total = summary["total_interactions"]
    st.subheader("Resumo do processamento", anchor=False)
    col1, col2 = st.columns(2)
    with col1:
        ui.metric_card(label="Interações processadas",
                       value=str(total), key=f"ps_total_{pid}")
    with col2:
        render_feeling_card(summary["predominant_feeling"])
    st.markdown("**Interações por origem**")
    breakdown = summary["sources_breakdown"]
    for col, (source, count) in zip(st.columns(len(breakdown)), breakdown.items()):
        with col:
            ui.metric_card(
                label=source,
                value=str(count),
                description=f"{count / total:.0%} do total" if total else "",
                key=f"ps_source_{pid}_{source}",
            )
    st.markdown("**Principais tópicos**")
    ui.badges([(topic, "secondary")
              for topic in summary["main_topics"]], key=f"ps_topics_{pid}")


def render_content_badges(content: dict) -> None:
    badges = [
        (TARGETS_ENUM.get(content["target"], content["target"]), "default"),
        ENGAGEMENT_BADGES[content["potential_engagement"]],
    ]
    if content["review_status"] in REVIEW_BADGES:
        badges.append(REVIEW_BADGES[content["review_status"]])
    ui.badges(badges, key=f"b_{content['id']}")


def render_pending_content(content: dict) -> None:
    with st.container(border=True):
        render_content_badges(content)
        content["body"] = st.text_area(
            content["title"], content["body"], key=f"body_{content['id']}", height=160)
        with st.container(horizontal=True, gap="xsmall"):
            ui.button("Aprovar", key=f"ok_{content['id']}", on_click=lambda c=content: set_review(
                c, "approved"))
            ui.button(
                "Rejeitar",
                key=f"no_{content['id']}",
                variant="destructive",
                on_click=lambda c=content: set_review(c, "rejected"),
            )


def split_body(body: str) -> tuple[str, str]:
    tags = " ".join(HASHTAG_TOKEN_RE.findall(body))
    text = HASHTAG_TOKEN_RE.sub("", body)
    text = HORIZONTAL_SPACING_RE.sub(" ", text)
    return EXTRA_NEWLINES_RE.sub("\n\n", text).strip(), tags


def render_copyable_parts(content: dict) -> None:
    text, tags = split_body(content["body"])
    parts = [("Título", content["title"]), ("Texto", text), ("Tags", tags)]
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
        ui.button(
            "Refazer revisão",
            key=f"undo_{content['id']}",
            variant="outline",
            on_click=lambda c=content: set_review(c, "pending"),
        )


def render_suggested_content(package: dict) -> None:
    contents = package["suggested_content"]
    st.subheader("Conteúdos sugeridos", anchor=False)
    counts = {status: sum(c["review_status"] == status for c in contents)
              for status in STATUSES_ENUM}
    status = ui.tabs(
        list(STATUSES_ENUM),
        value="pending",
        key="curation_status",
        label="Status",
        format_func=lambda s: f"{STATUSES_ENUM[s]} ({counts[s]})",
    )
    shown = [c for c in contents if c["review_status"] == status]
    if not shown:
        st.info(
            f"Nenhum conteúdo {STATUSES_ENUM[status].lower()} neste pacote.")
        return
    render = render_pending_content if status == "pending" else render_reviewed_content
    for content in shown:
        render(content)


def render_approved_upload(package: dict) -> None:
    if "provenance" not in package:
        return
    if not st.button(
        "Salvar pacote aprovado na OCI",
        disabled=not can_publish(package),
        key=f"publish_approved_{package['package_id']}",
    ):
        return
    with st.spinner("Salvando pacote aprovado..."):
        try:
            key = publish_approved_package(package)
        except RequestException:
            st.error(
                "Não foi possível confirmar a gravação na OCI. Você pode tentar novamente.")
            return
        except ValueError as error:
            st.error(str(error))
            return
    st.success(f"Pacote aprovado disponível na OCI em `{key}`.")


def render_curation() -> None:
    st.header("Curadoria")
    if "packages" not in st.session_state:
        st.session_state["packages"] = load_suggested_content()
    packages = {p["linked_batch_id"]                : p for p in st.session_state["packages"] + load_draft_packages()}
    if not packages:
        st.info("Nenhum pacote disponível para curadoria.")
        return
    request = st.session_state.get("nav_request", {})
    requested_batch = request.get("batch")
    default_batch = requested_batch if requested_batch in packages else next(
        iter(packages))
    batch_id = ui.tabs(
        list(packages),
        value=default_batch,
        key=f"curation_batch_{request.get('nonce', 0)}",
        label="Lote",
    )
    package = packages[batch_id]

    render_package_header(package)
    if provenance := package.get("provenance"):
        workflow = package["package_id"].split("-", 1)[0].upper()
        item = f"resposta {provenance['answer_id']}" if "answer_id" in provenance else f"publicação {provenance['post_id']}"
        st.caption(
            f"Triagem {workflow} · execução {provenance['execution_id']} · {item}"
        )
    render_processing_summary(package)
    render_reference_period(package)
    render_suggested_content(package)
    render_approved_upload(package)

    if st.button("Exportar aprovados (JSON)", key=f"export_{package['package_id']}"):
        path = export_approved(package, package["suggested_content"])
        st.success(f"Exportado em: {path}")


render_curation()
