"""Consulta do snapshot OCI já carregado no DuckDB."""

from datetime import timezone

import duckdb
import streamlit as st

from src.config import DATA_DIR
from src.services.processed_duckdb import DATABASE_LOCK, refresh_oci_database


def render_processed_data():
    st.header("Dados processados")
    st.caption("Registros coletados e avaliados, disponíveis para consulta por fonte e tag.")
    database = DATA_DIR / "communitylab_oci.duckdb"
    if st.button("Atualizar dados", type="primary"):
        try:
            with st.spinner("Carregando os dados da OCI..."):
                refresh_oci_database(database)
        except (duckdb.Error, ValueError, OSError):
            # Não expor exceções de configuração/rede: podem conter dados sensíveis.
            st.error("Não foi possível atualizar os dados. Confira as credenciais OCI, as permissões e a conexão.")
            st.caption("A última carga concluída foi preservada. Feche outros processos que estejam usando o banco.")
        else:
            st.success("Dados atualizados com sucesso.")
    if not database.is_file():
        st.info("Os dados ainda não foram carregados. Clique em Atualizar dados ou execute a carga abaixo na raiz do projeto.")
        st.code(
            "python -m src.services.processed_duckdb --oci --database data/communitylab_oci.duckdb",
            language="powershell",
        )
        return

    try:
        # Conexão curta por execução: não mantém recursos compartilhados entre sessões.
        with DATABASE_LOCK, duckdb.connect(str(database), read_only=True) as con:
            total, loaded_at = con.execute(
                "SELECT count(*), max(loaded_at) FROM v_processed"
            ).fetchone()
            if not total:
                st.info("A carga não contém registros. Atualize o banco e consulte novamente.")
                return
            sources = [row[0] for row in con.execute(
                "SELECT DISTINCT source FROM v_processed ORDER BY source"
            ).fetchall()]
            selected = st.selectbox("Fonte", ["Todas", *sources])
            # A tag de coleta está no nome do arquivo; difere das tags do conteúdo.
            tagged_records = r"""WITH tagged_records AS (
                SELECT *, nullif(regexp_extract(
                    replace(object_key, chr(92), '/'),
                    '(?:^|/)(?:processed_)?result_[^_]+_(.+)\.json$', 1
                ), '') AS tag FROM v_processed
            ) """
            tags = [row[0] for row in con.execute(
                tagged_records + "SELECT DISTINCT tag FROM tagged_records WHERE tag IS NOT NULL ORDER BY tag"
            ).fetchall()]
            selected_tag = st.selectbox("Tag", ["Todas", *tags])
            query = tagged_records + "SELECT source, tag, record_id, title, content, url, sentiment, suggested_route FROM tagged_records"
            parameters = []
            conditions = []
            if selected != "Todas":
                conditions.append("source = ?")
                parameters.append(selected)
            if selected_tag != "Todas":
                conditions.append("tag = ?")
                parameters.append(selected_tag)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            records = con.execute(query + " ORDER BY source, record_id", parameters).df()
    except duckdb.Error:
        st.error("Não foi possível consultar os dados. Confira se a carga terminou e se o banco está disponível.")
        st.caption("Feche processos que estejam gravando o banco e execute novamente a carga, se necessário.")
        return

    first, second = st.columns(2)
    first.metric("Registros no banco", total)
    second.metric("Registros exibidos", len(records))
    last_load = loaded_at.astimezone(timezone.utc).strftime('%d/%m/%Y %H:%M:%S') if loaded_at else 'não informada'
    st.caption(f"Última carga (UTC): {last_load}")
    if records.empty:
        st.info("Nenhum registro para a combinação de fonte e tag selecionada.")
    st.dataframe(
        records,
        hide_index=True,
        width="stretch",
        column_config={
            "source": "Fonte", "tag": "Tag", "record_id": "Identificador", "title": "Título",
            "content": "Conteúdo", "url": st.column_config.LinkColumn("Publicação original"),
            "sentiment": "Sentimento", "suggested_route": "Destino sugerido",
        },
    )
    st.caption("Os dados representam a última carga concluída. Campos sem informação aparecem vazios.")


render_processed_data()
