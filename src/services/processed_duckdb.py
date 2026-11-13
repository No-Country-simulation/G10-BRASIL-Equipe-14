"""Carga exploratória dos JSONs processados, localmente ou via S3/OCI."""

import argparse
import os
from pathlib import Path
from threading import RLock

import duckdb
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
# Compartilhado pelas sessões no mesmo processo Streamlit.
DATABASE_LOCK = RLock()


def refresh_oci_database(database):
    """Atualiza o snapshot sob o mesmo lock usado pelas consultas da interface."""
    with DATABASE_LOCK:
        database = Path(database)
        database.parent.mkdir(parents=True, exist_ok=True)
        with duckdb.connect(str(database)) as connection:
            pattern = configure_oci(connection)
            refresh(connection, pattern)


def configure_oci(connection):
    """Cria um secret temporário; não grava credenciais no banco."""
    load_dotenv(ROOT / ".env")
    required = ("OCI_S3_ACCESS_KEY_ID", "OCI_S3_SECRET_ACCESS_KEY")
    if any(not os.getenv(key) for key in required):
        raise ValueError("Configure OCI_S3_ACCESS_KEY_ID e OCI_S3_SECRET_ACCESS_KEY no .env.")
    region = os.getenv("OCI_REGION", "sa-saopaulo-1")
    namespace = os.getenv("OCI_NAMESPACE", "grue2tm7tuaq")
    bucket = os.getenv("OCI_BUCKET_NAME", "communitylab-assets")
    # Literais SQL escapados: CREATE SECRET não aceita parâmetros posicionais.
    def literal(value):
        return "'" + value.replace("'", "''") + "'"

    connection.execute("INSTALL httpfs")
    connection.execute("LOAD httpfs")
    options = {
        "KEY_ID": os.environ[required[0]],
        "SECRET": os.environ[required[1]],
        "REGION": region,
        "ENDPOINT": f"{namespace}.compat.objectstorage.{region}.oraclecloud.com",
        "URL_STYLE": "path",
        "SCOPE": f"s3://{bucket}/processed/",
    }
    connection.execute(
        "CREATE OR REPLACE SECRET communitylab_oci (TYPE s3, USE_SSL true, "
        + ", ".join(f"{key} {literal(value)}" for key, value in options.items())
        + ")"
    )
    return f"s3://{bucket}/processed/*.json"


def refresh(connection, pattern):
    """Substitui o snapshot completo; uma falha mantém a carga anterior."""
    connection.execute("BEGIN TRANSACTION")
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
            raise ValueError(f"{invalid} registros sem objeto JSON ou campo source.")
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
    except Exception:
        connection.execute("ROLLBACK")
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oci", action="store_true", help="Ler processed/ diretamente da OCI")
    parser.add_argument("--database", default="data/communitylab.duckdb")
    args = parser.parse_args()
    database = Path(args.database)
    database.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(database)) as connection:
        pattern = configure_oci(connection) if args.oci else str(ROOT / "data/processed/*.json")
        refresh(connection, pattern)
        print(f"DuckDB {duckdb.__version__} | Banco: {database}")
        for source, count in connection.execute(
            "SELECT source, count(*) FROM v_processed GROUP BY source ORDER BY source"
        ).fetchall():
            print(f"{source}: {count} registros")


if __name__ == "__main__":
    main()
