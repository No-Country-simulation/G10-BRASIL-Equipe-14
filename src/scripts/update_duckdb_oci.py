"""
To update with files from processed/, run:
python src/scripts/update_duckdb_oci.py --folder processed

To update with files from processed/routing/faq, run:
python src/scripts/update_duckdb_oci.py --folder processed/routing/success_case --database data/success_case.duckdb
"""

import argparse
from pathlib import Path
import duckdb


# Permite executar o arquivo diretamente a partir do diretório scripts.
from src.config import (
    DATABASE_PATH,
    OCI_BUCKET_NAME,
    OCI_NAMESPACE,
    OCI_REGION,
    OCI_S3_ACCESS_KEY_ID,
    OCI_S3_SECRET_ACCESS_KEY,
)


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def update_database(folder: str, database: Path) -> None:
    if not OCI_S3_ACCESS_KEY_ID or not OCI_S3_SECRET_ACCESS_KEY:
        raise ValueError(
            "Configure OCI_S3_ACCESS_KEY_ID e "
            "OCI_S3_SECRET_ACCESS_KEY no .env."
        )

    folder = folder.strip("/")
    if not folder or any(char in folder for char in "*?[]\\"):
        raise ValueError("Informe uma pasta sem curingas, como processed.")

    # Lê apenas JSONs diretamente nessa pasta, sem percorrer subpastas.
    pattern = f"s3://{OCI_BUCKET_NAME}/{folder}/*.json"

    database.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(database)) as connection:
        connection.execute("INSTALL httpfs")
        connection.execute("LOAD httpfs")

        options = {
            "KEY_ID": OCI_S3_ACCESS_KEY_ID,
            "SECRET": OCI_S3_SECRET_ACCESS_KEY,
            "REGION": OCI_REGION,
            "ENDPOINT": (
                f"{OCI_NAMESPACE}.compat.objectstorage."
                f"{OCI_REGION}.oraclecloud.com"
            ),
            "URL_STYLE": "path",
            "SCOPE": f"s3://{OCI_BUCKET_NAME}/{folder}/",
        }

        # Secret temporário: as credenciais não são persistidas no banco.
        connection.execute(
            "CREATE OR REPLACE TEMPORARY SECRET communitylab_oci "
            "(TYPE s3, USE_SSL true, "
            + ", ".join(
                f"{key} {sql_literal(value)}"
                for key, value in options.items()
            )
            + ")"
        )

        connection.execute("BEGIN TRANSACTION")
        try:
            connection.execute(
                """
                CREATE OR REPLACE TABLE processed_records AS
                SELECT
                    filename AS object_key,
                    json AS payload,
                    current_timestamp AS loaded_at
                FROM read_json_objects(
                    ?,
                    format = 'array',
                    filename = true
                )
                """,
                [pattern],
            )

            invalid_record_count = connection.execute(
                """
                SELECT count(*)
                FROM processed_records
                WHERE json_type(payload) IS DISTINCT FROM 'OBJECT'
                """
            ).fetchone()[0]

            if invalid_record_count:
                raise ValueError(
                    f"Foram encontrados {invalid_record_count} registros "
                    "que não são objetos JSON."
                )

            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise

        file_count, record_count = connection.execute(
            """
            SELECT count(DISTINCT object_key), count(*)
            FROM processed_records
            """
        ).fetchone()

        print(f"Banco atualizado: {database}")
        print(f"Origem: {pattern}")
        print(f"Arquivos com registros: {file_count}")
        print(f"Registros carregados: {record_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Atualiza um snapshot DuckDB com JSONs da OCI."
    )
    parser.add_argument("--folder", "--pasta", dest="folder", required=True)
    parser.add_argument(
        "--database",
        "--banco",
        dest="database",
        type=Path,
        default=DATABASE_PATH,
    )
    args = parser.parse_args()

    update_database(args.folder, args.database)
