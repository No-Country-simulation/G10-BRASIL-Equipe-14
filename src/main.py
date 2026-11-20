import streamlit as st

from src.config import LOGO_PATH, PAGE_TITLE
from src.ui import apply_theme
from src.ui_localization import localize_native_controls

HOME_PAGE = st.Page("views/home.py", title="Visão executiva", icon=":material/space_dashboard:", url_path="inicio", default=True)
SOURCES_PAGE = st.Page(
    "views/community_sources.py", title="Fontes da comunidade", icon=":material/groups:", url_path="fontes-da-comunidade"
)
INGESTION_PAGE = st.Page("views/ingestion.py", title="Ingestão de dados", icon=":material/upload_file:", url_path="ingestao")
CURATION_PAGE = st.Page("views/curation.py", title="Curadoria editorial", icon=":material/fact_check:", url_path="curadoria")
DASHBOARD_PAGE = st.Page(
    "views/sentiment_dashboard.py", title="Sentimentos e tópicos",
    icon=":material/monitoring:", url_path="sentimento-e-topicos",
)
PROCESSED_PAGE = st.Page(
    "views/processed_data.py", title="Dados processados", icon=":material/table_view:", url_path="dados-processados"
)


def configure_page() -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon=str(LOGO_PATH), layout="wide")


def main() -> None:
    configure_page()
    with st.sidebar:
        st.image(str(LOGO_PATH), width=150)
        st.caption("Inteligência de comunidades")
    sections = {"Principal": [HOME_PAGE], "Análise": [DASHBOARD_PAGE, PROCESSED_PAGE], "Operação": [INGESTION_PAGE, SOURCES_PAGE, CURATION_PAGE]}
    page = st.navigation(sections, position="hidden")
    with st.sidebar:
        for heading, pages in sections.items():
            st.caption(heading)
            for destination in pages:
                with st.container(key="navigation_current" if destination == page else f"navigation_{destination.url_path}"):
                    st.page_link(destination, label=destination.title, icon=destination.icon, width="stretch")
        st.markdown('<div class="cl-sidebar-footer">Ambiente de trabalho interno · Análise e curadoria</div>', unsafe_allow_html=True)
    apply_theme()
    st.markdown(f'<div class="cl-topbar"><strong>CommunityLab / {page.title}</strong><span>Inteligência editorial · Uso interno</span></div>', unsafe_allow_html=True)
    page.run()
    localize_native_controls()
    st.markdown('<div class="cl-footer">CommunityLab · Das conversas da comunidade ao conhecimento que orienta decisões.</div>', unsafe_allow_html=True)


main()
