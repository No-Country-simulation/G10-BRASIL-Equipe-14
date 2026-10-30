import re
from copy import deepcopy
from datetime import datetime

import streamlit as st
import streamlit_shadcn_ui as ui

from config import (
    FEELINGS_COLORS_ENUM,
    FEELINGS_ENUM,
    STATUSES_ENUM,
    TARGETS_ENUM,
    ENGAGEMENT_BADGES,
    PACKAGE_STATUS_BADGES,
    REVIEW_BADGES,
)

OUTPUT_PACKAGES_SAMPLE = [
    {
        "package_id": "pkg_2026_w42_001",
        "linked_batch_id": "lote-se-001",
        "status": "success",
        "reference_period": "2026-10-13T00:00:00Z/2026-10-20T00:00:00Z",
        "processing_summary": {
            "total_interactions": 128,
            "sources_breakdown": {"stackoverflow": 128},
            "predominant_feeling": "neutral",
            "main_topics": ["DuckDB / Engenharia de dados", "JSON Schema / Validação", "pandas"],
        },
        "suggested_content": [
            {
                "target": "linkedin",
                "title": "Caso de sucesso: migração para DuckDB",
                "body": "Uma equipe reduziu de 40 min para 90 s o processamento diário de logs ao "
                        "migrar do pandas para o DuckDB. Veja o que aprendemos com a comunidade.\n\n"
                        "#DuckDB #DataEngineering #Comunidade",
                "potential_engagement": "high",
            },
            {
                "target": "faq",
                "title": "Como ler JSON aninhado no DuckDB?",
                "body": "Use json_extract e unnest para achatar arrays aninhados direto no SQL.",
                "potential_engagement": "low",
            },
            {
                "target": "newsletter",
                "title": "Perguntas mais votadas da semana",
                "body": "As dúvidas sobre DuckDB e validação de JSON que mais geraram discussão no "
                        "Stack Exchange, com as respostas aceitas.",
                "potential_engagement": "medium",
            },
        ],
    },
    {
        "package_id": "pkg_2026_w42_002",
        "linked_batch_id": "lote-ma-002",
        "status": "success",
        "reference_period": "2026-10-13T00:00:00Z/2026-10-20T00:00:00Z",
        "processing_summary": {
            "total_interactions": 342,
            "sources_breakdown": {"mastodon": 342},
            "predominant_feeling": "positive",
            "main_topics": ["Open source", "LLMs em code review", "Observabilidade"],
        },
        "suggested_content": [
            {
                "target": "x/twitter",
                "title": "Projeto open source ganha tração",
                "body": "Um mantenedor brasileiro chegou a 1k estrelas após documentar bem o onboarding. "
                        "#opensource #comunidade",
                "potential_engagement": "high",
            },
            {
                "target": "discord",
                "title": "Qual a sua dica de documentação?",
                "body": "A semana mostrou que onboarding bem documentado atrai contribuidores. "
                        "Quem mais tem dicas para compartilhar?",
                "potential_engagement": "medium",
            },
            {
                "target": "newsletter",
                "title": "O que a comunidade discutiu esta semana",
                "body": "Três temas dominaram as conversas: observabilidade com OpenTelemetry, custos "
                        "de nuvem e o uso de LLMs em code review.",
                "potential_engagement": "medium",
            },
        ],
    },
    {
        "package_id": "pkg_2026_w42_003",
        "linked_batch_id": "lote-hn-003",
        "status": "suspended",
        "reference_period": "2026-10-13T00:00:00Z/2026-10-20T00:00:00Z",
        "processing_summary": {
            "total_interactions": 76,
            "sources_breakdown": {"hackernews": 76},
            "predominant_feeling": "positive",
            "main_topics": ["Show HN", "IA", "Rust"],
        },
        "suggested_content": [
            {
                "target": "blog",
                "title": "Show HN da semana: benchmark open source de LLMs",
                "body": "Um novo conjunto de benchmarks abertos para LLMs chamou a atenção da "
                        "comunidade, com 145 pontos e 42 comentários.",
                "potential_engagement": "high",
            },
            {
                "target": "linkedin",
                "title": "Rust e IA: o que o Hacker News está comentando",
                "body": "Ferramentas de IA escritas em Rust aparecem cada vez mais nas discussões da "
                        "semana. #Rust #IA",
                "potential_engagement": "medium",
            },
        ],
    },
    {
        "package_id": "pkg_2026_w41_001",
        "linked_batch_id": "lote-se-004",
        "status": "success",
        "reference_period": "2026-10-06T00:00:00Z/2026-10-13T00:00:00Z",
        "processing_summary": {
            "total_interactions": 87,
            "sources_breakdown": {"stackoverflow": 87},
            "predominant_feeling": "negative",
            "main_topics": ["n8n / Webhooks", "Docker Compose / Volumes"],
        },
        "suggested_content": [
            {
                "target": "faq",
                "title": "FAQ: containers e volumes no Docker Compose",
                "body": "As dúvidas mais frequentes sobre persistência de dados com volumes nomeados "
                        "e bind mounts, com exemplos prontos para copiar.",
                "potential_engagement": "low",
            },
            {
                "target": "blog",
                "title": "n8n webhook retorna 404 em produção?",
                "body": "O endpoint de teste e o de produção são diferentes: ative o workflow antes de "
                        "chamar a URL /webhook/.",
                "potential_engagement": "medium",
            },
        ],
    },
]

def load_suggested_content() -> list[dict]:
    packages = deepcopy(OUTPUT_PACKAGES_SAMPLE)
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
        st.title(package["linked_batch_id"], anchor=False)
        ui.badges(
            [PACKAGE_STATUS_BADGES[package["status"]], (package["package_id"], "outline")],
            key=f"pkg_status_{package['package_id']}",
        )


def render_reference_period(package: dict) -> None:
    st.markdown(f"**Período de referência:** {format_period(package['reference_period'])}")


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
    st.subheader("Resumo do processamento", anchor=False)
    col1, col2 = st.columns(2)
    with col1:
        ui.metric_card(label="Interações processadas", value=str(summary["total_interactions"]), key=f"ps_total_{pid}")
    with col2:
        render_feeling_card(summary["predominant_feeling"])
    st.markdown("**Interações por origem**")
    breakdown = summary["sources_breakdown"]
    for col, (source, count) in zip(st.columns(len(breakdown)), breakdown.items()):
        with col:
            ui.metric_card(
                label=source,
                value=str(count),
                description=f"{count / summary['total_interactions']:.0%} do total",
                key=f"ps_source_{pid}_{source}",
            )
    st.markdown("**Principais tópicos**")
    ui.badges([(topic, "secondary") for topic in summary["main_topics"]], key=f"ps_topics_{pid}")


def render_content_badges(content: dict) -> None:
    badges = [(TARGETS_ENUM[content["target"]], "default"), ENGAGEMENT_BADGES[content["potential_engagement"]]]
    if content["review_status"] in REVIEW_BADGES:
        badges.append(REVIEW_BADGES[content["review_status"]])
    ui.badges(badges, key=f"b_{content['id']}")


def render_pending_content(content: dict) -> None:
    with st.container(border=True):
        render_content_badges(content)
        content["body"] = st.text_area(content["title"], content["body"], key=f"body_{content['id']}", height=160)
        with st.container(horizontal=True, gap="xsmall"):
            ui.button("Aprovar", key=f"ok_{content['id']}", on_click=lambda c=content: set_review(c, "approved"))
            ui.button(
                "Rejeitar",
                key=f"no_{content['id']}",
                variant="destructive",
                on_click=lambda c=content: set_review(c, "rejected"),
            )


def split_body(body: str) -> tuple[str, str]:
    tags = " ".join(re.findall(r"#\w+", body))
    text = re.sub(r"[ \t]*#\w+", "", body)
    return re.sub(r"\n{3,}", "\n\n", text).strip(), tags


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
            "Voltar para pendentes",
            key=f"undo_{content['id']}",
            variant="outline",
            on_click=lambda c=content: set_review(c, "pending"),
        )


def render_suggested_content(package: dict) -> None:
    contents = package["suggested_content"]
    st.subheader("Conteúdos sugeridos", anchor=False)
    counts = {status: sum(c["review_status"] == status for c in contents) for status in STATUSES_ENUM}
    status = ui.tabs(
        list(STATUSES_ENUM),
        value="pending",
        key="curation_status",
        label="Status",
        format_func=lambda s: f"{STATUSES_ENUM[s]} ({counts[s]})",
    )
    shown = [c for c in contents if c["review_status"] == status]
    if not shown:
        st.info(f"Nenhum conteúdo {STATUSES_ENUM[status].lower()} neste pacote.")
        return
    render = render_pending_content if status == "pending" else render_reviewed_content
    for content in shown:
        render(content)

def render_curation() -> None:
    st.header("Curadoria")
    if "packages" not in st.session_state:
        st.session_state["packages"] = load_suggested_content()
    packages = {p["linked_batch_id"]: p for p in st.session_state["packages"]}
    request = st.session_state.get("nav_request", {})
    batch_id = ui.tabs(
        list(packages),
        value=request.get("batch", next(iter(packages))),
        key=f"curation_batch_{request.get('nonce', 0)}",
        label="Lote",
    )
    package = packages[batch_id]

    render_package_header(package)
    render_processing_summary(package)
    render_reference_period(package)
    render_suggested_content(package)


render_curation()
