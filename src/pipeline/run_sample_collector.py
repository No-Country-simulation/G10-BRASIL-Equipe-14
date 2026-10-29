import logging
from datetime import datetime, timezone
from src.pipeline.sample_collector import DataSourceCollector
from src.config import DEFAULT_LIMIT, DEFAULT_PERIOD, DEFAULT_TAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("Iniciando coleta integrada...")
    collector = DataSourceCollector()

    formatted_date = datetime.fromtimestamp(DEFAULT_PERIOD, tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    # 1. Stack Exchange
    try:
        logger.info(f"\n[1/3] Coletando dados do Stack Exchange em {formatted_date}...")
        se_data = collector.fetch_stack_exchange(tag=DEFAULT_TAG, limit=DEFAULT_LIMIT)
        collector.save_to_samples("stack_exchange", se_data)
    except Exception as e:
        logger.error(f"Erro no Stack Exchange: {e}")

    # 2. Hacker News
    try:
        logger.info(f"\n[2/3] Coletando dados do Hacker News em {formatted_date}...")
        hn_data = collector.fetch_hacker_news(query=DEFAULT_TAG, limit=DEFAULT_LIMIT)
        collector.save_to_samples("hacker_news", hn_data)
    except Exception as e:
        logger.error(f"Erro no Hacker News: {e}")

    # 3. Mastodon
    try:
        logger.info(f"\n[3/3] Coletando dados do Mastodon em {formatted_date}...")
        mt_data = collector.fetch_mastodon(hashtag=DEFAULT_TAG, limit=DEFAULT_LIMIT)
        collector.save_to_samples("mastodon", mt_data)
    except Exception as e:
        logger.error(f"Erro no Mastodon: {e}")

    logger.info("Coleta integrada concluída com sucesso.")


if __name__ == "__main__":
    main()
