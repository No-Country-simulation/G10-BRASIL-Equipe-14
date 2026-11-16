import logging

import pandas as pd
import streamlit as st
from src.ui import EDITORIAL_LABELS, SENTIMENT_LABELS, SOURCE_LABELS, THEME_LABELS, metric_card, page_header, style_chart

from src.services.sentiment_dashboard import EDITORIALS, SENTIMENTS, THEMES, load_snapshot
from src.views.dashboard_chat import render_chat
from src.services.sentiment_treemap import build_treemap

LABELS = EDITORIAL_LABELS


def reorder_treemap(category):
    order = st.session_state["treemap_order"].copy()
    previous = order.index(category)
    target = st.session_state[f"treemap_position_{category}"] - 1
    displaced = order[target]
    order[previous], order[target] = order[target], order[previous]
    st.session_state["treemap_order"] = order
    st.session_state[f"treemap_position_{displaced}"] = previous + 1


def render_dashboard():
    page_header("Sentimentos e tópicos", "Investigue sinais, encontre dúvidas recorrentes e priorize oportunidades editoriais a partir das avaliações da IA.", "Análise / Indicadores")
    with st.container(horizontal=True, vertical_alignment="center", key="data_actions"):
        if st.button("Recarregar dados", icon=":material/refresh:"):
            st.rerun()
        freshness = st.empty()
    try:
        frame, quality = load_snapshot()
    except Exception:
        logging.getLogger(__name__).exception("Falha ao consultar snapshot de sentimento")
        st.error("Não foi possível consultar o DuckDB. Confira a carga e feche outros processos que estejam atualizando o banco.")
        st.code("python scripts/atualizar_duckdb_oci.py --pasta processed", language="powershell")
        return
    if frame.empty:
        st.info("A base consolidada não contém interações. Carregue os arquivos JSON de processed/.")
        return
    loaded_at = frame.loaded_at.max()
    freshness.caption(f"Última carga: {pd.to_datetime(loaded_at, utc=True).tz_convert('America/Sao_Paulo'):%d/%m/%Y %H:%M} (Brasília) · {quality['records']} registros de origem")
    with st.container(border=True):
        st.markdown("**Recorte da análise**")
        a, b, c = st.columns(3)
        sources = a.multiselect("Fontes", sorted(frame.source.unique()), format_func=lambda value: SOURCE_LABELS.get(value, value), key="analysis_sources", placeholder="Selecione as fontes")
        themes = b.multiselect("Temas da coleta", THEMES + sorted(set(frame.theme) - set(THEMES)), format_func=lambda value: THEME_LABELS.get(value, value), key="analysis_themes", placeholder="Selecione os temas")
        routes = c.multiselect("Destino editorial sugerido", EDITORIALS, format_func=lambda x: LABELS.get(x, x), key="analysis_routes", placeholder="Selecione os destinos")
        a, b = st.columns(2)
        topics = a.multiselect("Tópicos extraídos pela IA", sorted({t for values in frame.topics for t in values}), key="analysis_topics", placeholder="Selecione os tópicos")
        review = b.selectbox("Revisão humana", ["Todas", "Requer revisão", "Não sinalizada", "Não informado"], key="analysis_review")
        dated = frame.created_at.dropna()
        use_period = st.checkbox("Filtrar por data da interação", disabled=dated.empty)
        if use_period:
            period = st.date_input("Período", value=(dated.min().date(), dated.max().date()), min_value=dated.min().date(), max_value=dated.max().date())
            if len(period) != 2:
                st.info("Selecione o início e o fim do período.")
                return
            frame = frame[frame.created_at.notna() & (frame.created_at.dt.date >= period[0]) & (frame.created_at.dt.date <= period[1])]
    for column, selected in [("source", sources), ("theme", themes), ("editorial", routes)]:
        if selected:
            frame = frame[frame[column].isin(selected)]
    if topics:
        frame = frame[frame.topics.map(lambda values: bool(set(values) & set(topics)))]
    if review != "Todas":
        frame = frame[frame.needs_review.isna() if review == "Não informado" else frame.needs_review.eq(review == "Requer revisão")]
    chat_filters = {
        "sources": sources, "themes": themes, "editorials": routes,
        "topics": topics, "review": review,
        "period": [d.isoformat() for d in period] if use_period else None,
    }
    if frame.empty:
        st.info("Nenhuma interação corresponde aos filtros selecionados.")
        render_chat(frame, chat_filters, loaded_at, quality)
        return
    unique = frame.drop_duplicates("identity", keep="last")
    counts = unique[unique.sentiment.isin(SENTIMENTS)].sentiment.value_counts()
    leaders = counts[counts == counts.max()].index.tolist() if not counts.empty else []
    dominant = " / ".join(SENTIMENT_LABELS.get(value, value) for value in leaders) if leaders else "Sem avaliação"
    top = frame.groupby("theme").identity.nunique().sort_values(ascending=False)
    with st.container(key="workspace_kpis"):
        a, b, c, d = st.columns(4, gap="small")
    with a:
        metric_card("Interações únicas", len(unique), "No recorte selecionado")
    with b:
        metric_card("Sentimento predominante", dominant, "Empates exibem todos os líderes")
    with c:
        metric_card("Tema mais frequente", THEME_LABELS.get(top.index[0], top.index[0]), "Tema da coleta por interações únicas")
    with d:
        metric_card("Requer revisão humana", int(unique.needs_review.eq(True).sum()), "Sinalização da IA; não é decisão humana")
    st.caption("Tema da coleta indica a busca de origem; tópicos são assuntos extraídos pela IA. Uma interação pode aparecer em vários temas, mas conta uma vez no total geral. Revisão sinalizada não equivale a aprovação ou rejeição humana.")
    if quality["conflicts"]:
        st.warning(f"Interações com sentimentos diferentes entre registros: {quality['conflicts']}. No resumo, usamos a última carga e, em empate, o último arquivo em ordem alfabética. Consulte o detalhamento por tema.")
    st.subheader("Mapa das avaliações")
    st.caption("Ative as categorias e escolha suas posições: 1 é o nível mais amplo e 4 é o mais detalhado. Ao mudar uma posição, as categorias trocam de lugar. Clique em Atualizar para aplicar a configuração ao treemap.")
    categories = [("source", "Fonte"), ("theme", "Tema da coleta"), ("editorial", "Editorial"), ("sentiment", "Sentimento")]
    order = st.session_state.setdefault("treemap_order", [category for category, _ in categories])
    selected_levels = []
    with st.container(key="treemap_controls"):
        controls = st.columns([1, 1.2, 1, 1, .8], vertical_alignment="center")
    for column, (category, label) in zip(controls[:4], categories):
        position_key = f"treemap_position_{category}"
        st.session_state.setdefault(position_key, order.index(category) + 1)
        with column.container(horizontal=True, vertical_alignment="center"):
            st.selectbox(f"Posição de {label}", [1, 2, 3, 4], key=position_key, label_visibility="collapsed", width=76, on_change=reorder_treemap, args=(category,))
            if st.checkbox(label, value=True, key=f"treemap_{category}"):
                selected_levels.append(category)
    selected_levels = [category for category in order if category in selected_levels]
    applied_levels = st.session_state.setdefault("treemap_applied_levels", [category for category, _ in categories])
    if controls[4].button("Atualizar", key="treemap_apply", type="primary", icon=":material/refresh:", width="stretch"):
        applied_levels = selected_levels.copy()
        st.session_state["treemap_applied_levels"] = applied_levels
    if selected_levels != applied_levels:
        st.caption("Há alterações pendentes. Clique em Atualizar para aplicá-las ao gráfico.")
    if applied_levels:
        category_labels = dict(categories)
        st.caption("Hierarquia atual: " + " → ".join(category_labels[category] for category in applied_levels))
        label_maps = {"source": SOURCE_LABELS, "theme": THEME_LABELS, "editorial": EDITORIAL_LABELS, "sentiment": SENTIMENT_LABELS}
        diagram = build_treemap(frame, applied_levels, label_maps)
        st.plotly_chart(style_chart(diagram), width="stretch", theme=None, config={"displayModeBar": False})
        st.caption("A área dos blocos representa o número de associações. Clique em um bloco para ampliar; use o caminho no topo do gráfico para voltar. Cada categoria mantém suas cores ao alterar a ordem ou os filtros; sentimentos não representam estados de aprovação, alerta ou erro.")
    else:
        st.info("Selecione ao menos uma categoria para exibir o treemap.")
    association_count = len(frame.drop_duplicates(["identity", "theme"], keep="last"))
    st.caption(f"{association_count} associações a temas, correspondentes a {len(unique)} interações únicas. Uma interação coletada em vários temas conta uma vez em cada tema. Desativar um nível agrupa essas associações sem alterar o total representado.")
    with st.expander("Interações e origem dos dados"):
        st.caption(f"{len(frame)} associações a temas · {unique.created_at.isna().sum()} interações sem data · {unique.sentiment.eq('Sem avaliação').sum()} sem sentimento válido")
        details = frame[["source", "record_id", "theme", "sentiment", "editorial", "topics", "needs_review", "strength", "confidence", "relevance", "created_at", "summary", "content", "url", "object_key"]].copy()
        details["topics"] = details.topics.map(lambda values: ", ".join(values))
        query = st.text_input("Pesquisar nas interações", placeholder="Busque por texto, resumo, fonte ou tópico")
        if query:
            details = details[details.astype(str).apply(lambda column: column.str.contains(query, case=False, regex=False)).any(axis=1)]
        display_details = details.copy()
        for column, labels in [("source", SOURCE_LABELS), ("theme", THEME_LABELS), ("sentiment", SENTIMENT_LABELS), ("editorial", EDITORIAL_LABELS)]:
            display_details[column] = display_details[column].map(lambda value: labels.get(value, value))
        st.dataframe(display_details, hide_index=True, width="stretch", column_config={
            "source": "Fonte", "record_id": "Identificador", "theme": "Tema da coleta",
            "sentiment": "Sentimento", "editorial": "Destino editorial", "topics": "Tópicos",
            "needs_review": st.column_config.CheckboxColumn("Requer revisão"),
            "strength": st.column_config.NumberColumn("Intensidade do sentimento", format="%.2f", help="Pontuação atribuída pelo agente, de 0 a 1. Mede a intensidade, não se o sentimento é positivo ou negativo."),
            "confidence": st.column_config.NumberColumn("Confiança na avaliação", format="%.2f", help="Confiança atribuída pelo agente à classificação, de 0 a 1. Não representa uma probabilidade de acerto calibrada."),
            "relevance": "Relevância",
            "created_at": st.column_config.DatetimeColumn("Data da interação", format="DD/MM/YYYY HH:mm [UTC]"),
            "summary": "Resumo", "content": "Conteúdo", "object_key": "Arquivo de origem",
            "url": st.column_config.LinkColumn("Publicação"),
        })
        st.download_button("Exportar recorte em CSV", details.to_csv(index=False).encode("utf-8-sig"), "communitylab-interacoes.csv", "text/csv", icon=":material/download:")
        st.caption("Dados lidos somente do consolidado communitylab_oci.duckdb. Os bancos de roteamento contêm cópias e execuções anteriores e não são somados ao resumo. Para buscar novas coletas, atualize o DuckDB pelo script e recarregue esta página.")

    render_chat(frame, chat_filters, loaded_at, quality)


render_dashboard()
