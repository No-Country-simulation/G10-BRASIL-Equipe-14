import argparse
import sys
from pathlib import Path

import duckdb


# Permite executar o arquivo diretamente a partir do diretório scripts.
if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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


def atualizar(pasta: str, banco: Path) -> None:
    if not OCI_S3_ACCESS_KEY_ID or not OCI_S3_SECRET_ACCESS_KEY:
        raise ValueError(
            "Configure OCI_S3_ACCESS_KEY_ID e "
            "OCI_S3_SECRET_ACCESS_KEY no .env."
        )

    pasta = pasta.strip("/")
    if not pasta or any(char in pasta for char in "*?[]\\"):
        raise ValueError("Informe uma pasta sem curingas, como processed.")

    # Lê apenas JSONs diretamente nessa pasta, sem percorrer subpastas.
    pattern = f"s3://{OCI_BUCKET_NAME}/{pasta}/*.json"

    banco.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(banco)) as con:
        con.execute("INSTALL httpfs")
        con.execute("LOAD httpfs")

        options = {
            "KEY_ID": OCI_S3_ACCESS_KEY_ID,
            "SECRET": OCI_S3_SECRET_ACCESS_KEY,
            "REGION": OCI_REGION,
            "ENDPOINT": (
                f"{OCI_NAMESPACE}.compat.objectstorage."
                f"{OCI_REGION}.oraclecloud.com"
            ),
            "URL_STYLE": "path",
            "SCOPE": f"s3://{OCI_BUCKET_NAME}/{pasta}/",
        }

        # Secret temporário: as credenciais não são persistidas no banco.
        con.execute(
            "CREATE OR REPLACE TEMPORARY SECRET communitylab_oci "
            "(TYPE s3, USE_SSL true, "
            + ", ".join(
                f"{key} {sql_literal(value)}"
                for key, value in options.items()
            )
            + ")"
        )

        con.execute("BEGIN TRANSACTION")
        try:
            con.execute(
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

            invalidos = con.execute(
                """
                SELECT count(*)
                FROM processed_records
                WHERE json_type(payload) IS DISTINCT FROM 'OBJECT'
                """
            ).fetchone()[0]

            if invalidos:
                raise ValueError(
                    f"Foram encontrados {invalidos} registros "
                    "que não são objetos JSON."
                )

            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise

        arquivos, registros = con.execute(
            """
            SELECT count(DISTINCT object_key), count(*)
            FROM processed_records
            """
        ).fetchone()

        print(f"Banco atualizado: {banco}")
        print(f"Origem: {pattern}")
        print(f"Arquivos com registros: {arquivos}")
        print(f"Registros carregados: {registros}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Atualiza um snapshot DuckDB com JSONs da OCI."
    )
    parser.add_argument("--pasta", required=True)
    parser.add_argument(
        "--banco",
        type=Path,
        default=DATABASE_PATH,
    )
    args = parser.parse_args()

    atualizar(args.pasta, args.banco)

# Para atualizar com os arquivos de processed/, execute:
# python scripts/atualizar_duckdb_oci.py --pasta processed

# Para atualizar com os arquivos de processed/routing/faq, execute:
# python scripts/atualizar_duckdb_oci.py --pasta processed/routing/success_case --banco data/success_case.duckdb