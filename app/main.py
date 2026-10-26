import streamlit as st
from dotenv import load_dotenv

load_dotenv()

PAGE_TITLE = "CommunityLab"

HOME_PAGE = st.Page("pages/home.py", title="Início", icon=":material/home:", url_path="inicio", default=True)
SOURCES_PAGE = st.Page(
    "pages/community_sources.py", title="Fontes da comunidade", icon=":material/groups:", url_path="fontes-da-comunidade"
)
CURATION_PAGE = st.Page("pages/curation.py", title="Curadoria", icon=":material/fact_check:", url_path="curadoria")


def configure_page() -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon="🧪", layout="wide")


def main() -> None:
    configure_page()
    st.navigation([HOME_PAGE, SOURCES_PAGE, CURATION_PAGE]).run()


main()
