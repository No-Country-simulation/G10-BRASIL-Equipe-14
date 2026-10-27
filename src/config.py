from pathlib import Path

# Configuração de diretórios relativos
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROMPTS_DATA_DIR = DATA_DIR / "prompts"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLES_DATA_DIR = DATA_DIR / "samples"
SCHEMAS_DATA_DIR = DATA_DIR / "schemas"
INPUT_SCHEMA_PATH = SCHEMAS_DATA_DIR / "input_schema.json"
OUTPUT_SCHEMA_PATH = SCHEMAS_DATA_DIR / "output_schema.json"

# Definindo os parâmetros padrões de coleta
DEFAULT_LIMIT = 10
DEFAULT_TAG = "artificial-intelligence"  # Tag padrão para coleta do Stack Exchange
SAMPLES_DEFAULT_PERIOD = (
    1761027120  # Timestamp fixo (samples) em 2025-10-21 22:32:00 UTC
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
}

# Parâmetros do Stack Exchange API (https://api.stackexchange.com/docs)
STACKEXCHANGE_BASE_URL = "https://api.stackexchange.com/2.3/questions"

STACKEXCHANGE_PARAMS = {
    "site": "stackoverflow",
    "order": "desc",
    "sort": "votes",
    "tagged": DEFAULT_TAG,
    "pagesize": DEFAULT_LIMIT,
    "fromdate": SAMPLES_DEFAULT_PERIOD,
    "filter": "default",
}

# Parâmetros do Hacker News API (https://hn.algolia.com/api/)
HACKER_NEWS_BASE_URL = "https://hn.algolia.com/api/v1/search_by_date"

HACKER_NEWS_PARAMS = {
    "query": DEFAULT_TAG,
    "tags": "story",
    "hitsPerPage": DEFAULT_LIMIT,
    "numericFilters": f"created_at_i>={SAMPLES_DEFAULT_PERIOD}",
}

# Parâmetros do Mastodon API (https://docs.joinmastodon.org/api/rest/)
MASTODON_INSTANCE = "mastodon.social"
MASTODON_BASE_URL = f"https://{MASTODON_INSTANCE}/api/v1/timelines/tag/{DEFAULT_TAG}"
MASTODON_PARAMS = {
    "limit": DEFAULT_LIMIT,
    "from_date": SAMPLES_DEFAULT_PERIOD,
}
