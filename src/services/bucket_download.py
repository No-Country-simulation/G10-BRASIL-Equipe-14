"""Download autenticado de arquivos pelo WF05."""

import io
import os
import zipfile
from typing import Literal

import requests

from src.config import N8N_BASE_URL, N8N_DOWNLOAD_TIMEOUT


FolderType = Literal["raw/", "processed/"]


class BucketDownloadError(requests.RequestException):
    """Falha HTTP ou de transporte no download pelo WF05."""


def download_folder(folder: FolderType) -> bytes:
    if folder not in ("raw/", "processed/"):
        raise ValueError("Pasta inválida.")
    api_key = os.getenv("N8N_API_KEY", "")
    if not api_key:
        raise ValueError("Configure N8N_API_KEY no .env para acessar o WF05.")
    url = os.getenv("N8N_DOWNLOAD_WEBHOOK_URL") or f"{N8N_BASE_URL}/webhook/wf05-download-bucket-OCI"
    try:
        with requests.get(
            url, params={"folder": folder},
            headers={"communitylab-api-key": api_key}, timeout=N8N_DOWNLOAD_TIMEOUT,
        ) as response:
            response.raise_for_status()
            content = response.content
    except requests.RequestException as exc:
        raise BucketDownloadError(
            "Falha na comunicação com o webhook do WF05.",
            response=exc.response,
        ) from exc
    if not zipfile.is_zipfile(io.BytesIO(content)):
        raise ValueError("O WF05 não retornou um ZIP válido.")
    return content
