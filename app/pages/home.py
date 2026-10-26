import streamlit as st

PAGE_TITLE = "CommunityLab"
PROJECT_BRIEF = (
    "O CommunityLab é um ecossistema inteligente de automação que transforma o fluxo contínuo de "
    "discussões e dúvidas de comunidades técnicas em ativos estruturados de valor educacional e marketing."
)
GITHUB_PROJECT_URL = "https://github.com/No-Country-simulation/G10-BRASIL-Equipe-14"

def render_home() -> None:
    st.markdown(
        f"""
        <div style="text-align:center; padding:2.5rem 0 1rem;">
            <span style="display:inline-block; border:1px solid rgba(128,128,128,.4); background:rgba(128,128,128,.12);
                         border-radius:999px; padding:4px 16px; font-size:.8rem;">
                Hackathon ONE · G10 Brasil · Equipe 14
            </span>
            <h1 style="font-size:clamp(2.5rem, 7vw, 5rem); font-weight:800; letter-spacing:-0.03em;
                       line-height:1.05; margin:1.25rem 0 1rem; padding:0;">
                🚀 {PAGE_TITLE}
            </h1>
            <p style="font-size:1.5rem; font-weight:600; max-width:48rem; margin:0 auto 1rem;">
                Motor inteligente de transformação e distribuição para comunidades digitais
            </p>
            <p style="font-size:1.1rem; opacity:.75; max-width:40rem; margin:0 auto;">
                {PROJECT_BRIEF}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(horizontal=True, horizontal_alignment="center", gap="small"):
        if st.button("Começar →", type="primary", key="home_start"):
            st.switch_page("pages/community_sources.py")
        st.link_button("GitHub", GITHUB_PROJECT_URL)


render_home()
