import logging
import pandas as pd
import streamlit as st
from src.services.sentiment_dashboard import load_snapshot
from src.ui import metric_card, page_header


def render_home():
    page_header("Visão executiva", "Identifique sinais da comunidade, priorize a revisão e transforme dúvidas em conteúdo útil.",
                "Inteligência de comunidades")
    try:
        frame, quality = load_snapshot()
    except Exception:
        logging.getLogger(__name__).info(
            "Snapshot indisponível", exc_info=True)
        frame = pd.DataFrame()
    if frame.empty:
        st.info("Ainda não há dados consolidados disponíveis. Comece pela ingestão ou conheça o fluxo nas fontes de demonstração.")
    else:
        st.caption(
            f"Última carga: {pd.to_datetime(frame.loaded_at.max(), utc=True).tz_convert('America/Sao_Paulo'):%d/%m/%Y %H:%M} (Brasília) · Base consolidada")
        unique = frame.drop_duplicates("identity", keep="last")
        figures = [("Interações únicas", len(unique), "Conversas na base consolidada"), ("Fontes monitoradas", unique.source.nunique(), "Origens com dados disponíveis"), ("Requer revisão", int(
            unique.needs_review.eq(True).sum()), "Sinalizações para avaliação humana"), ("Oportunidades de FAQ", int(unique.editorial.eq("faq").sum()), "Encaminhamentos sugeridos pela IA")]
        with st.container(key="workspace_kpis"):
            kpi_columns = st.columns(4, gap="small")
        for col, values in zip(kpi_columns, figures):
            with col:
                metric_card(*values)
        with st.container(border=True):
            st.subheader("Prioridades de atenção")
            st.caption(
                "Sinais do consolidado para orientar a próxima análise da equipe.")
            pending = int(unique.needs_review.eq(True).sum())
            if pending:
                st.warning(
                    f"Interações sinalizadas para revisão humana: {pending}.   \n Investigue o contexto antes de definir o encaminhamento editorial.")
            else:
                st.info(
                    "Nenhuma interação sinalizada para revisão neste consolidado.")
            if quality["conflicts"]:
                st.warning(
                    f"Interações com avaliações de sentimento divergentes: {quality['conflicts']}.")
            st.page_link("views/sentiment_dashboard.py",
                         label="Investigar sentimentos e tópicos", icon=":material/arrow_forward:")
    st.subheader("Próximos passos")
    st.caption("Acesse a etapa de trabalho que você precisa realizar.")
    steps = [("01 · Preparar", "Envie interações e valide os dados antes do processamento.", "views/ingestion.py", "Adicionar dados"), 
             ("02 · Analisar", "Explore sentimentos, assuntos recorrentes e destinos editoriais.", "views/sentiment_dashboard.py", "Explorar indicadores"), 
             ("03 · Revisar", "Avalie sugestões para FAQ, newsletter e redes sociais.", "views/curation.py", "Abrir curadoria")]
    for col, (title, description, path, label) in zip(st.columns(3), steps):
        with col, st.container(border=True):
            st.subheader(title)
            st.write(description)
            st.page_link(path, label=label, icon=":material/arrow_forward:")
    st.caption("Fontes e curadoria apresentam exemplos demonstrativos. As revisões permanecem nesta sessão; aprovação não publica conteúdo.")


render_home()
