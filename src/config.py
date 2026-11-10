import os
from pathlib import Path
import re
from dotenv import load_dotenv

# Configuração de diretórios relativos
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROMPTS_DATA_DIR = DATA_DIR / "prompts"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VALIDATION_DIR = SRC_DIR / "validation"
SAMPLES_DATA_DIR = DATA_DIR / "samples"
SCHEMAS_DATA_DIR = DATA_DIR / "schemas"
INPUT_SCHEMA_PATH = SCHEMAS_DATA_DIR / "input_schema.json"
OUTPUT_SCHEMA_PATH = SCHEMAS_DATA_DIR / "output_schema.json"
CASES_DIR = PROMPTS_DATA_DIR / "cases"
OUTPUTS_DIR = PROMPTS_DATA_DIR / "outputs"
PROMPTS_ROUTER = PROMPTS_DATA_DIR / "router"
DEFAULT_CASES = [
    CASES_DIR / "router_cases_sinteticos.json",
    CASES_DIR / "router_cases_reais.json",
]


# Arquivo .env
try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass


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

# Configuração de prompts e schemas
ROUTER_VERSION = "0.4.1"  # Atualizado com o arquivo de spec router-prompt.md

PROMPT_ENUMS = {
    "type": {
        "job_achievement",
        "testimonial",
        "technical_question",
        "course_feedback",
        "debate",
        "noise",
    },
    "sentiment": {"positive", "neutral", "negative"},
    "topic_category": {
        "frontend",
        "backend",
        "data",
        "ai_ml",
        "devops_cloud",
        "mobile",
        "dev_tools",
        "career",
        "other",
    },
    "original_language": {"pt", "es", "en", "other"},
    "suggested_route": {
        "success_case",
        "faq",
        "newsletter_only",
        "moderation",
        "discard",
    },
}

REQUIRED_FIELDS = set(PROMPT_ENUMS) | {
    "id",
    "source",
    "topics",
    "has_answer",
    "relevance_score",
    "summary",
    "justification",
}
SPECIAL_KEYS = {"suggested_route_in", "min_score", "max_score"}


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

# Configuração de regex para remover code fences
CODE_FENCE_PATTERN = re.compile(
    r"^\s*```(?:json)?\s*(.*?)\s*```\s*$",
    re.IGNORECASE | re.DOTALL,
)

# Configuração de palavras-chave sensíveis para segurança
SECURITY_MARKERS = (
    "cpf ",
    "cartão de crédito",
    "credit card",
    "api key",
    "api_key",
    "secret key",
    "access token",
    "bearer token",
    "jwt",
    "private key",
    "connection string",
    "senha",
    "password",
    "credencial exposta",
    "credencial vazada",
    "dados pessoais expostos",
    "dados pessoais vazados",
    "vazamento de dados",
    "acidentalmente publiquei",
    "accidentally published",
)

# Configuração de mensagens de erro que podem ser tratadas com retry
RETRYABLE_ERROR_PREFIXES = (
    "saída deve ser um objeto JSON",
    "campos ausentes:",
    "Campos adicionais",
    "topics deve ter",
    "relevance_score inválido",
    "summary deve ser",
    "summary com",
    "type:",
    "sentiment:",
    "topic_category:",
    "original_language:",
    "suggested_route:",
)
