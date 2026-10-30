import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from config import PAGE_TITLE

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

load_dotenv()

HOME_PAGE = st.Page("views/home.py", title="Início", icon=":material/home:", url_path="inicio", default=True)
SOURCES_PAGE = st.Page(
    "views/community_sources.py", title="Fontes da comunidade", icon=":material/groups:", url_path="fontes-da-comunidade"
)
CURATION_PAGE = st.Page("views/curation.py", title="Curadoria", icon=":material/fact_check:", url_path="curadoria")


def configure_page() -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon="🧪", layout="wide")


def main() -> None:
    configure_page()
    st.navigation([HOME_PAGE, SOURCES_PAGE, CURATION_PAGE]).run()


main()
