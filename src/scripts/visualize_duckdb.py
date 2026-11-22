"""Serve DuckDB UI while keeping the project's analytical database read-only."""

import argparse
from pathlib import Path
from threading import Event
import duckdb


# Permite executar o arquivo diretamente a partir do diretório scripts.
from src.config import DATABASE_PATH, PROJECT_ROOT, UI_DATABASE_PATH


def main(database: Path = DATABASE_PATH):
    if not database.is_absolute():
        database = PROJECT_ROOT / database
    if not database.is_file():
        raise FileNotFoundError(f"Banco não encontrado: {database}")

    with duckdb.connect(str(UI_DATABASE_PATH)) as connection:
        connection.execute("INSTALL ui")
        connection.execute("LOAD ui")
        path_literal = str(database).replace("'", "''")
        connection.execute(
            f"ATTACH '{path_literal}' AS communitylab (READ_ONLY)")
        connection.execute("CALL start_ui_server()")
        print("DuckDB UI: http://localhost:4213", flush=True)
        print("Banco communitylab conectado em modo somente leitura.", flush=True)
        print("Mantenha este terminal aberto. Pressione Ctrl+C para encerrar.", flush=True)
        try:
            while True:
                Event().wait(1)
        except KeyboardInterrupt:
            print("\nEncerrando DuckDB UI...", flush=True)
        finally:
            connection.execute("CALL stop_ui_server()")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Inicia a DuckDB UI para inspeção de um banco.")
    parser.add_argument(
        "--database",
        type=Path,
        default=DATABASE_PATH,
        help="Arquivo DuckDB a inspecionar. Caminhos relativos partem da raiz do projeto.",
    )
    args = parser.parse_args()
    main(args.database)
