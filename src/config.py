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
DEFAULT_TAG = "artificial-intelligence"
DEFAULT_PERIOD = 1761027120  # Timestamp do período de 1 ano fixo em formato Unix. Data: 2025-10-21 06:12:00 UTC

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
    "fromdate": DEFAULT_PERIOD,
    "filter": "default",
}

# Parâmetros do Hacker News API (https://hn.algolia.com/api/)
HACKER_NEWS_BASE_URL = "https://hn.algolia.com/api/v1/search_by_date"

HACKER_NEWS_PARAMS = {
    "query": DEFAULT_TAG,
    "tags": "story",
    "hitsPerPage": DEFAULT_LIMIT,
    "numericFilters": f"created_at_i>={DEFAULT_PERIOD}",
}

# Parâmetros do Mastodon API (https://docs.joinmastodon.org/api/rest/)
MASTODON_INSTANCE = "social.espeweb.net"
MASTODON_BASE_URL = "https://{instance}/api/v1/timelines/tag/{hashtag}"
MASTODON_PARAMS = {
    "limit": DEFAULT_LIMIT,
}

# Streamlit
PAGE_TITLE = "CommunityLab"

PROJECT_BRIEF = (
    "O CommunityLab é um ecossistema inteligente de automação que transforma o fluxo contínuo de "
    "discussões e dúvidas de comunidades técnicas em ativos estruturados de valor educacional e marketing."
)

GITHUB_PROJECT_URL = "https://github.com/No-Country-simulation/G10-BRASIL-Equipe-14"

PROCESSING_SECONDS = 3

FEELINGS_COLORS_ENUM = {
    "positive": ("#dcf5e3", "#b4e3c3"),
    "neutral": ("#fff4cc", "#f2e0a0"),
    "negative": ("#fde0e0", "#f4baba"),
}

FEELINGS_ENUM = {
    "positive": "😊 Positivo",
    "neutral": "😐 Neutro",
    "negative": "😟 Negativo",
}

STATUSES_ENUM = {
    "pending": "Pendentes",
    "approved": "Aprovados",
    "rejected": "Rejeitados"
}

TARGETS_ENUM = {
    "linkedin": "LinkedIn",
    "newsletter": "Newsletter",
    "faq": "FAQ",
    "instagram": "Instagram",
    "x/twitter": "X/Twitter",
    "discord": "Discord",
    "blog": "Blog",
    "mastodon": "Mastodon",
}

REVIEW_BADGES = {
    "approved": ("aprovado", "default"),
    "rejected": ("rejeitado", "destructive")
}

PACKAGE_STATUS_BADGES = {
    "success": ("✅ Sucesso", "default"),
    "suspended": ("⏸️ Suspenso", "secondary"),
    "error": ("❌ Erro", "destructive"),
}

ENGAGEMENT_BADGES = {
    "low": ("📉 engajamento baixo", "outline"),
    "medium": ("📊 engajamento médio", "secondary"),
    "high": ("🔥 engajamento alto", "default"),
}
