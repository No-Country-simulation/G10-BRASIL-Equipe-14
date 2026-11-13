"""Download autenticado de arquivos pelo WF05."""

import io
import os
import zipfile

import requests

from src.config import N8N_BASE_URL


def download_folder(folder: str) -> bytes:
    if folder not in ("raw/", "processed/"):
        raise ValueError("Pasta inválida.")
    api_key = os.getenv("N8N_API_KEY", "")
    if not api_key:
        raise ValueError("Configure N8N_API_KEY no .env para acessar o WF05.")
    url = os.getenv("N8N_DOWNLOAD_WEBHOOK_URL") or f"{N8N_BASE_URL}/webhook/wf05-download-bucket-OCI"
    with requests.get(
        url, params={"folder": folder},
        headers={"communitylab-api-key": api_key}, timeout=120,
    ) as response:
        response.raise_for_status()
        content = response.content
    if not zipfile.is_zipfile(io.BytesIO(content)):
        raise ValueError("O WF05 não retornou um ZIP válido.")
    return content
