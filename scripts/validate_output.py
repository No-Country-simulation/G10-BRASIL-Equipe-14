"""Valida o pacote de distribuição final contra data/schemas/output_schema.json.

Uso (CI ou local):
    python -m scripts.validate_output caminho/pacote.json
    python -m scripts.validate_output --week 2026-W44      # busca o último pacote da semana no bucket

Códigos de saída: 0 = válido, 1 = inválido, 2 = erro de uso, arquivo ou bucket.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import oci
from oci.object_storage import ObjectStorageClient

from src.config import OCI_ASSETS_PREFIX, OCI_BUCKET_NAME, OCI_NAMESPACE, OUTPUT_SCHEMA_PATH
from src.services.oci_storage import _latest_pacote
from src.validation.schema_validator import load_json, validate_data


def validate_output(data_path: str | Path, schema_path: str | Path = OUTPUT_SCHEMA_PATH) -> list[str]:
    """Retorna a lista de erros (vazia se o pacote for válido)."""
    return validate_data(load_json(data_path), load_json(schema_path))


def fetch_from_bucket(object_key: str, client=None, dest_dir: str | Path | None = None) -> Path:
    """Baixa um objeto do bucket e devolve o caminho do arquivo local."""
    client = client or ObjectStorageClient(oci.config.from_file())
    response = client.get_object(
        OCI_NAMESPACE, OCI_BUCKET_NAME, object_key,
        retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
    )
    dest = Path(dest_dir or tempfile.mkdtemp()) / Path(object_key).name
    dest.write_bytes(response.data.content)
    return dest


def fetch_latest_pacote(week_label: str, client=None, dest_dir: str | Path | None = None) -> Path:
    """Baixa o pacote mais recente da semana (ex.: 2026-W44). Levanta FileNotFoundError se não houver."""
    client = client or ObjectStorageClient(oci.config.from_file())
    found = _latest_pacote(client, OCI_BUCKET_NAME, f"{OCI_ASSETS_PREFIX}/{week_label}/")
    if found is None:
        raise FileNotFoundError(f"Nenhum pacote no bucket para a semana {week_label}.")
    name, _sha = found
    return fetch_from_bucket(name, client=client, dest_dir=dest_dir)


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida o pacote de saída contra o output_schema.json.")
    parser.add_argument("data", nargs="?", help="Caminho local do JSON do pacote a validar.")
    parser.add_argument("--week", help="Semana no formato YYYY-Www: valida o último pacote do bucket.")
    parser.add_argument("--schema", default=str(OUTPUT_SCHEMA_PATH), help="Schema de saída (padrão: output_schema.json).")
    args = parser.parse_args(argv)

    if bool(args.data) == bool(args.week):
        print("Erro: informe um arquivo local ou --week, não os dois.", file=sys.stderr)
        return 2

    try:
        if args.week:
            data_path = fetch_latest_pacote(args.week)
        else:
            data_path = Path(args.data)
            if not data_path.is_file():
                print(f"Erro: arquivo não encontrado: {data_path}", file=sys.stderr)
                return 2
        errors = validate_output(data_path, args.schema)
    except FileNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:  # JSON malformado
        print(f"Erro: JSON inválido: {exc}", file=sys.stderr)
        return 2
    except oci.exceptions.ServiceError as exc:  # bucket, permissão ou rede
        print(f"Erro no bucket: {exc.message}", file=sys.stderr)
        return 2

    if errors:
        print(f"Inválido: {data_path}")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Válido: {data_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
