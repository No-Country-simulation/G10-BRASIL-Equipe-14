"""Carga exploratória dos JSONs processados, localmente ou via S3/OCI."""

import argparse
import sys
from pathlib import Path
from threading import RLock

import duckdb

from src.config import (
    OCI_BUCKET_NAME,
    OCI_NAMESPACE,
    OCI_REGION,
    OCI_S3_ACCESS_KEY_ID,
    OCI_S3_SECRET_ACCESS_KEY,
    PROJECT_ROOT,
)

# Compartilhado pelas sessões no mesmo processo Streamlit.
DATABASE_LOCK = RLock()


def refresh_oci_database(database: str | Path) -> None:
    """Atualiza o snapshot sob o mesmo lock usado pelas consultas da interface."""
    db_path = Path(database)
    with DATABASE_LOCK:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with duckdb.connect(str(db_path)) as connection:
            pattern = configure_oci(connection)
            refresh(connection, pattern)


def configure_oci(connection: duckdb.DuckDBPyConnection) -> str:
    """Cria um secret temporário; não grava credenciais no banco."""
    if not OCI_S3_ACCESS_KEY_ID.strip() or not OCI_S3_SECRET_ACCESS_KEY.strip():
        raise ValueError(
            "Configure OCI_S3_ACCESS_KEY_ID e OCI_S3_SECRET_ACCESS_KEY no .env.")

    endpoint = f"{OCI_NAMESPACE}.compat.objectstorage.{OCI_REGION}.oraclecloud.com"
    scope = f"s3://{OCI_BUCKET_NAME}/processed/"

    connection.execute("INSTALL httpfs")
    connection.execute("LOAD httpfs")
    connection.execute(
        """
        CREATE OR REPLACE TEMPORARY SECRET communitylab_oci (
            TYPE s3, KEY_ID ?, SECRET ?, REGION ?, ENDPOINT ?,
            URL_STYLE 'path', USE_SSL true, SCOPE ?
        )
        """,
        [OCI_S3_ACCESS_KEY_ID, OCI_S3_SECRET_ACCESS_KEY, OCI_REGION, endpoint, scope],
    )
    return f"{scope}*.json"


def refresh(connection, pattern) -> None:
    """Substitui o snapshot completo; uma falha mantém a carga anterior."""
    connection.execute("BEGIN TRANSACTION")
    committed = False
    try:
        connection.execute(
            "CREATE OR REPLACE TABLE processed_records AS "
            "SELECT filename AS object_key, json AS payload, current_timestamp AS loaded_at "
            "FROM read_json_objects(?, format='array', filename=true)",
            [pattern],
        )
        invalid = connection.execute(
            "SELECT count(*) FROM processed_records WHERE json_type(payload) != 'OBJECT' "
            "OR json_extract_string(payload, '$.source') IS NULL"
        ).fetchone()[0]
        if invalid:
            raise ValueError(
                f"{invalid} registros sem objeto JSON ou campo source.")
        connection.execute("""
            CREATE OR REPLACE VIEW v_processed AS
            SELECT
                CASE WHEN json_exists(payload, '$.clean_text') THEN 'mastodon'
                     ELSE payload->>'$.source' END AS source,
                coalesce(payload->>'$.comment_id', payload->>'$.source_id',
                         payload->>'$.post_id') AS record_id,
                coalesce(payload->>'$.title_question', payload->>'$.post.title') AS title,
                coalesce(payload->>'$.clean_text', payload->>'$.comment.text',
                         payload->>'$.body_question') AS content,
                coalesce(payload->>'$.url', payload->>'$.link_question',
                         payload->>'$.post.url') AS url,
                coalesce(payload->>'$.sentiment', payload->>'$.comment.sentiment',
                         payload->>'$.answers[0].sentiment') AS sentiment,
                coalesce(payload->>'$.suggested_route', payload->>'$.editorial.suggested_route') AS suggested_route,
                object_key, loaded_at, payload
            FROM processed_records
        """)
        connection.execute("COMMIT")
        committed = True
    except (duckdb.Error, ValueError, OSError) as exc:
        exc.add_note(
            "Falha ao atualizar o snapshot de dados processados no DuckDB.")
        raise
    finally:
        if not committed:
            failure = sys.exception()
            try:
                connection.execute("ROLLBACK")
            except duckdb.Error as rollback_error:
                if failure is None:
                    raise
                failure.add_note(
                    f"Falha no rollback do snapshot ({type(rollback_error).__name__}).")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oci", action="store_true",
                        help="Ler processed/ diretamente da OCI")
    parser.add_argument("--database", default="data/communitylab.duckdb")
    args = parser.parse_args()
    database = Path(args.database)
    database.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(database)) as connection:
        pattern = configure_oci(connection) if args.oci else str(
            PROJECT_ROOT / "data/processed/*.json")
        refresh(connection, pattern)
        print(f"DuckDB {duckdb.__version__} | Banco: {database}")
        for source, count in connection.execute(
            "SELECT source, count(*) FROM v_processed GROUP BY source ORDER BY source"
        ).fetchall():
            print(f"{source}: {count} registros")


if __name__ == "__main__":
    main()
