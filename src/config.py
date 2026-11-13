import os
from pathlib import Path
from dotenv import load_dotenv

# Configuração de diretórios relativos
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent

ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROMPTS_DATA_DIR = DATA_DIR / "prompts"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLES_DATA_DIR = DATA_DIR / "samples"
SCHEMAS_DATA_DIR = DATA_DIR / "schemas"
INPUT_SCHEMA_PATH = SCHEMAS_DATA_DIR / "input_schema.json"
OUTPUT_SCHEMA_PATH = SCHEMAS_DATA_DIR / "output_schema.json"
FIXTURES_DIR = DATA_DIR / "fixtures"
CASES_DIR = PROMPTS_DATA_DIR / "cases"
OUTPUTS_DIR = PROMPTS_DATA_DIR / "outputs"
PROMPTS_ADAPTERS_DIR = PROMPTS_DATA_DIR / "adapters"
ADAPTER_CASES = CASES_DIR / "adapters_cases.json"

# Definindo os parâmetros padrões de coleta
DEFAULT_LIMIT = 10
DEFAULT_TAG = "artificial-intelligence"
DEFAULT_PERIOD = (
    1760929200  # 2025-10-20 03:00 UTC, período fixo definido pelo time (Rodrigo, 02/11)
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

# Armazenamento OCI (S2-04). Valores da infraestrutura do projeto.
# Credenciais NÃO ficam aqui: são lidas do ~/.oci/config ou de variáveis de ambiente.
OCI_REGION = os.getenv("OCI_REGION", "sa-saopaulo-1")
OCI_NAMESPACE = os.getenv("OCI_NAMESPACE", "grue2tm7tuaq")
OCI_BUCKET_NAME = os.getenv("OCI_BUCKET_NAME", "communitylab-assets")
OCI_ASSETS_PREFIX = (
    "ativos"  # objeto final: ativos/YYYY-semana-XX/pacote-distribuicao.json
)
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
    "rejected": "Rejeitados",
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
    "rejected": ("rejeitado", "destructive"),
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

N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678").rstrip("/")
N8N_INGESTION_WEBHOOK_PATH = os.getenv(
    "N8N_INGESTION_WEBHOOK_PATH", "webhook/ingestion"
).strip("/")
N8N_INGESTION_WEBHOOK_URL = (
    os.getenv("N8N_INGESTION_WEBHOOK_URL")
    or f"{N8N_BASE_URL}/{N8N_INGESTION_WEBHOOK_PATH}"
)
N8N_REQUEST_TIMEOUT = float(os.getenv("N8N_REQUEST_TIMEOUT", "30"))

CSV_DELIMITERS = ",;\t|"
INGESTION_TEXT_AREA_NAME = "texto colado"
MAX_INGESTION_TEXT_CHARS = 10_000
MAX_UPLOAD_FILE_COUNT = 10
MAX_UPLOAD_FILE_SIZE_MB = 10
MAX_UPLOAD_FILE_SIZE_BYTES = MAX_UPLOAD_FILE_SIZE_MB * 1024 * 1024
MAX_TOTAL_UPLOAD_SIZE_MB = 100
MAX_TOTAL_UPLOAD_SIZE_BYTES = MAX_TOTAL_UPLOAD_SIZE_MB * 1024 * 1024

SCORE_TIP = "Média do score de relevância (0–100) das interações do lote."

# Configuração de prompts e schemas
ADAPTER_SOCIAL_VERSION = "0.4.0"
ADAPTER_NEWSLETTER_FAQ_VERSION = "0.4.0"

# Configurações de Adapters
SCHEMA_KEYS = {"target", "title", "body", "potential_engagement"}
TARGETS_SCHEMA = {
    "linkedin",
    "newsletter",
    "faq",
    "instagram",
    "mastodon",
    "x/twitter",
    "discord",
    "blog",
}

CHANNEL_PROMPTS = {
    "linkedin": "adapter_linkedin.md",
    "x/twitter": "adapter_x_twitter.md",
    "mastodon": "adapter_mastodon.md",
    "instagram": "adapter_instagram.md",
    "discord": "adapter_discord.md",
    "blog": "adapter_blog.md",
    "faq": "adapter_faq.md",
    "newsletter": "adapter_newsletter.md",
}

# canal: (mín. caracteres, máx. caracteres, mín. hashtags, máx. hashtags, máx. emojis, máx. caracteres do título)
CHANNEL_LIMITS = {
    "linkedin": (600, 1300, 3, 5, 3, 80),
    "x/twitter": (1, 280, 1, 2, None, 80),
    "mastodon": (1, 500, 0, 2, None, 80),
    "instagram": (1, 2200, 5, 10, 5, 120),
    "discord": (1, 2000, 0, 2, None, 80),
    "faq": (1, 1200, 0, 0, None, 80),
    "newsletter": (1, 3000, 0, 0, None, 60),
    "blog": (500, 5000, 0, 5, None, 120),
}

FORBIDDEN = [
    "é com grande alegria",
    "gratidão!",
    "nada nos dá mais orgulho",
    "venha fazer parte",
    "não perca",
    "esperamos que esteja bem",
    "imperdível",
    "clique aqui",
]

REVIEW_TAG = "[PRECISA DE REVISÃO TÉCNICA]"

# Configurações de LLM Providers
DEFAULT_TEMPERATURE = 0.0
GEMINI_TEMPERATURE = 1.0

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

GROQ_MODEL = os.getenv("GROQ_MODEL", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Configurações de retry e timeout para chamadas HTTP
RETRYABLE_STATUS_CODES = {429, 500, 503}
DEFAULT_TIMEOUT_SECONDS = 90
RETRY_BACKOFF_SECONDS = 5
MAX_RETRY_WAIT_SECONDS = 30
