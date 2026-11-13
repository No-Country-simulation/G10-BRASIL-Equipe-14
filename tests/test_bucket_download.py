import io
import zipfile
from unittest.mock import MagicMock

import pytest

from src.services import bucket_download


@pytest.mark.parametrize('folder', ['raw/', 'processed/'])
def test_download_passes_folder_and_auth(monkeypatch, folder):
    monkeypatch.setenv('N8N_API_KEY', 'test-key')
    content = io.BytesIO()
    with zipfile.ZipFile(content, 'w') as archive:
        archive.writestr('sample.json', '[]')
    response = MagicMock()
    response.__enter__.return_value = response
    response.content = content.getvalue()
    get = MagicMock(return_value=response)
    monkeypatch.setattr(bucket_download.requests, 'get', get)
    assert bucket_download.download_folder(folder) == content.getvalue()
    assert get.call_args.kwargs['params'] == {'folder': folder}
    assert get.call_args.kwargs['headers'] == {'communitylab-api-key': 'test-key'}
    response.raise_for_status.assert_called_once()


def test_invalid_folder_and_missing_key(monkeypatch):
    monkeypatch.delenv('N8N_API_KEY', raising=False)
    with pytest.raises(ValueError, match='Pasta inválida'):
        bucket_download.download_folder('../')
    with pytest.raises(ValueError, match='N8N_API_KEY'):
        bucket_download.download_folder('raw/')


def test_rejects_non_zip_response(monkeypatch):
    monkeypatch.setenv('N8N_API_KEY', 'test-key')
    response = MagicMock()
    response.__enter__.return_value = response
    response.content = b'{"error": "failed"}'
    monkeypatch.setattr(bucket_download.requests, 'get', lambda *a, **k: response)
    with pytest.raises(ValueError, match='ZIP válido'):
        bucket_download.download_folder('raw/')
