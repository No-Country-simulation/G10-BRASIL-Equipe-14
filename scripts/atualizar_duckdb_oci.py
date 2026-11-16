import argparse
import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def atualizar(pasta: str, banco: Path) -> None:
    load_dotenv(ROOT / ".env")

    access_key = os.getenv("OCI_S3_ACCESS_KEY_ID")
    secret_key = os.getenv("OCI_S3_SECRET_ACCESS_KEY")

    if not access_key or not secret_key:
        raise ValueError(
            "Configure OCI_S3_ACCESS_KEY_ID e "
            "OCI_S3_SECRET_ACCESS_KEY no .env."
        )

    region = os.getenv("OCI_REGION", "sa-saopaulo-1")
    namespace = os.environ["OCI_NAMESPACE"]
    bucket = os.getenv("OCI_BUCKET_NAME", "communitylab-assets")

    pasta = pasta.strip("/")
    if not pasta or any(char in pasta for char in "*?[]\\"):
        raise ValueError("Informe uma pasta sem curingas, como processed.")

    # Lê apenas JSONs diretamente nessa pasta, sem percorrer subpastas.
    pattern = f"s3://{bucket}/{pasta}/*.json"

    banco.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(banco)) as con:
        con.execute("INSTALL httpfs")
        con.execute("LOAD httpfs")

        options = {
            "KEY_ID": access_key,
            "SECRET": secret_key,
            "REGION": region,
            "ENDPOINT": (
                f"{namespace}.compat.objectstorage."
                f"{region}.oraclecloud.com"
            ),
            "URL_STYLE": "path",
            "SCOPE": f"s3://{bucket}/{pasta}/",
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
        default=ROOT / "data/communitylab_oci.duckdb",
    )
    args = parser.parse_args()

    atualizar(args.pasta, args.banco)

# Para atualizar com os arquivos de processed/, execute:
# python scripts/atualizar_duckdb_oci.py --pasta processed

# Para atualizar com os arquivos de processed/routing/faq, execute:
# python scripts/atualizar_duckdb_oci.py --pasta processed/routing/success_case --banco data/success_case.duckdb