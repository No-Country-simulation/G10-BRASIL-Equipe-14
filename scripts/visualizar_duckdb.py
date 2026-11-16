"""Serve DuckDB UI while keeping the project's analytical database read-only."""

from pathlib import Path
from threading import Event

import duckdb


def main():
    root = Path(__file__).resolve().parents[1]
    database = root / "data/communitylab_oci.duckdb"
    if not database.is_file():
        raise FileNotFoundError(f"Banco não encontrado: {database}")

    with duckdb.connect(str(root / "data/duckdb_ui.duckdb")) as connection:
        connection.execute("INSTALL ui")
        connection.execute("LOAD ui")
        path_literal = str(database).replace("'", "''")
        connection.execute(f"ATTACH '{path_literal}' AS communitylab (READ_ONLY)")
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
    main()
