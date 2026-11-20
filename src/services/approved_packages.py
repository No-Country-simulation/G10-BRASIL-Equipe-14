"""Persistência do pacote aprovado na OCI."""

import json
import re
from datetime import datetime, timezone

from src.config import OCI_BUCKET_NAME, OUTPUT_SCHEMA_PATH
from src.services.raw_ingestion import request_oci_object
from src.validation.schema_validator import load_json, validate_data

ASSET_FIELDS = ("target", "title", "body", "potential_engagement")


def approved_assets(package):
    return [
        {field: item[field] for field in ASSET_FIELDS}
        for item in package["suggested_content"]
        if item["review_status"] == "approved"
    ]


def can_publish(package):
    return (
        "provenance" in package
        and len({asset["target"] for asset in approved_assets(package)}) >= 2
    )


def publish_approved_package(package):
    if not can_publish(package):
        raise ValueError("Aprove ativos de pelo menos dois formatos para salvar o pacote.")
    execution_id = str(package["provenance"].get("execution_id", ""))
    package_id = package["package_id"]
    if (
        not re.fullmatch(r"[0-9]+", execution_id)
        or package_id not in {f"wf09-{execution_id}", f"wf10-{execution_id}", f"wf11-{execution_id}"}
    ):
        raise ValueError("O lote não está vinculado a uma execução válida de triagem.")
    key = f"assets/approved/s4-01/{package_id}/distribution-package.json"
    payload = {
        "package_id": package_id,
        "status": "success",
        "reference_period": package["reference_period"],
        "processing_summary": package["processing_summary"],
        "suggested_content": approved_assets(package),
        "storage": {"bucket": OCI_BUCKET_NAME, "object_path": key, "status": "success"},
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if validate_data(payload, load_json(OUTPUT_SCHEMA_PATH)):
        raise ValueError("O pacote aprovado não atende ao esquema de saída do projeto.")

    response = request_oci_object("PUT", key, json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    if 200 <= response.status_code < 300:
        return key
    if response.status_code != 412:
        raise ValueError(f"A OCI não confirmou a gravação (HTTP {response.status_code}).")

    existing = request_oci_object("GET", key)
    if existing.status_code != 200:
        raise ValueError("A chave já existe na OCI e não foi possível conferir seu conteúdo.")
    stored = existing.json()
    if not isinstance(stored, dict):
        raise ValueError("O objeto existente não contém um pacote válido.")
    if {k: v for k, v in stored.items() if k != "created_at"} != {
        k: v for k, v in payload.items() if k != "created_at"
    }:
        raise ValueError("Já existe um pacote diferente para este lote na OCI.")
    return key
