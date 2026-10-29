import json
import requests
import logging
from pathlib import Path

from src.config import (
    MASTODON_BASE_URL,
    SAMPLES_DATA_DIR,
    HEADERS,
    DEFAULT_LIMIT,
    DEFAULT_TAG,
    STACKEXCHANGE_BASE_URL,
    STACKEXCHANGE_PARAMS,
    HACKER_NEWS_BASE_URL,
    HACKER_NEWS_PARAMS,
    MASTODON_INSTANCE,
    MASTODON_BASE_URL,
    MASTODON_PARAMS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSourceCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_stack_exchange(
        self, tag: str = DEFAULT_TAG, limit: int = DEFAULT_LIMIT
    ) -> list:
        tag = tag or DEFAULT_TAG
        limit = limit or DEFAULT_LIMIT
        url = STACKEXCHANGE_BASE_URL
        params = STACKEXCHANGE_PARAMS.copy()
        params["tagged"] = tag or DEFAULT_TAG
        params["pagesize"] = limit or DEFAULT_LIMIT

        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])

    def fetch_hacker_news(
        self, query: str = DEFAULT_TAG, limit: int = DEFAULT_LIMIT
    ) -> list:
        query = query or DEFAULT_TAG
        limit = limit or DEFAULT_LIMIT
        url = HACKER_NEWS_BASE_URL
        params = HACKER_NEWS_PARAMS.copy()
        params["query"] = query or DEFAULT_TAG
        params["hitsPerPage"] = limit or DEFAULT_LIMIT

        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("hits", [])

    def fetch_mastodon(
        self,
        instance: str = MASTODON_INSTANCE,
        hashtag: str = DEFAULT_TAG,
        limit: int = DEFAULT_LIMIT,
    ) -> list:
        inst = instance or MASTODON_INSTANCE
        tag_clean = (hashtag or DEFAULT_TAG).replace("-", "")

        url = MASTODON_BASE_URL.format(instance=inst, hashtag=tag_clean)
        params = MASTODON_PARAMS.copy()
        params["limit"] = limit or DEFAULT_LIMIT

        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []

    def save_to_samples(self, source_name: str, records: list) -> Path:

        if not isinstance(records, list):
            raise ValueError(
                f"Esperado uma lista de registros para '{source_name}', recebido: {type(records)}"
            )

        if len(records) == 0:
            logger.warning(
                f"[{source_name}] A busca não retornou nenhum registro! "
                f"O arquivo será salvo com uma lista vazia []."
            )

        clean_source_name = source_name.replace("_", "")
        file_path = SAMPLES_DATA_DIR / f"sample_{clean_source_name}_api.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        logger.info(f"[{source_name}] Salvos {len(records)} registros em {file_path}")
        return file_path
