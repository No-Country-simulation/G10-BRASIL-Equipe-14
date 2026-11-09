"""Valida o pacote de distribuição final contra data/schemas/output_schema.json.

Uso (CI ou local):
    python -m scripts.validate_output caminho/pacote.json
    python -m scripts.validate_output caminho/pacote.json --schema outro_schema.json

Códigos de saída: 0 = válido, 1 = inválido, 2 = erro de uso/arquivo.

TODO (dependente do módulo OCI da S2-04): fetch_from_bucket() ainda não existe.
Enquanto não houver, a validação roda sobre arquivo local.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.config import OUTPUT_SCHEMA_PATH
from src.validation.schema_validator import load_json, validate_data


def validate_output(data_path: str | Path, schema_path: str | Path = OUTPUT_SCHEMA_PATH) -> list[str]:
    """Retorna a lista de erros (vazia se o pacote for válido)."""
    return validate_data(load_json(data_path), load_json(schema_path))


def fetch_from_bucket(object_path: str) -> Path:  # pragma: no cover - placeholder
    raise NotImplementedError("Aguardando o helper de download OCI (S2-04).")


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida o pacote de saída contra o output_schema.json.")
    parser.add_argument("data", help="Caminho do JSON do pacote a validar.")
    parser.add_argument("--schema", default=str(OUTPUT_SCHEMA_PATH), help="Schema de saída (padrão: output_schema.json).")
    args = parser.parse_args(argv)

    if not Path(args.data).is_file():
        print(f"Erro: arquivo não encontrado: {args.data}", file=sys.stderr)
        return 2

    try:
        errors = validate_output(args.data, args.schema)
    except ValueError as exc:  # JSON malformado
        print(f"Erro: JSON inválido em {args.data}: {exc}", file=sys.stderr)
        return 2

    if errors:
        print(f"Inválido: {args.data}")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Válido: {args.data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
