from datetime import datetime
import re

# Configurações de regex para validação de conteúdo
EMOJI_RE = re.compile(
    "[\U0001f300-\U0001faff\U00002600-\U000027bf\U0001f000-\U0001f2ff]"
)
HASHTAG_RE = re.compile(r"(?<![\w&/])#(\w+)")
URL_RE = re.compile(r"https?://\S+")
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)*")
MENTION_RE = re.compile(r"(?<![\w.@/])@[A-Za-z0-9_][\w.]*")
VERSION_RE = re.compile(
    r"(?<![\w])v?\d+(?:\.\d+){1,}(?![\w])",
    re.IGNORECASE,
)

# Configuração de regex para remover code fences
CODE_FENCE_PATTERN = re.compile(
    r"^\s*```(?:json)?\s*(.*?)\s*```\s*$",
    re.IGNORECASE | re.DOTALL,
)

# Remove pontuação e espaços para normalização de dígitos
DIGIT_CLEANUP_RE = re.compile(r"[.,\s]")

# Isola o ano atual para evitar falsos positivos numéricos em textos


def get_current_year_re():
    current_year = str(datetime.now().year)
    return re.compile(rf"(?<![\d-]){current_year}(?![\d-]s)")


# Valida se o título de FAQ começa com as perguntas permitidas
FAQ_TITLE_START_RE = re.compile(r"(Como|Por que|O que)\b")

# Padrões para sanitização e limpeza de HTML em textos de canais
HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")

# Padrões de identificadores e nomes gerados pelos workflows
QUEUE_EXECUTION_FILE_RE = re.compile(r"_(\d+)\.json$")
EXECUTION_ID_RE = re.compile(r"[0-9]+")
DRAFT_PACKAGE_RE = re.compile(r"wf(?:09|10|11)-\d+")
UPLOAD_TAG_RE = re.compile(r"[a-z0-9]+(?:[ -][a-z0-9]+)*")
RECURRENCE_TAG_RE = re.compile(r"s4-01-recorrencia-upload[0-9a-f]{16}")

# Padrões de análise e formatação de conteúdo
NUMERIC_TIMESTAMP_RE = re.compile(r"\d+(?:\.\d+)?")
PROCESSED_THEME_RE = re.compile(
    r"^(processed_)?result_(mastodon|stackoverflow|hackernews)_"
)
HASHTAG_TOKEN_RE = re.compile(r"(?<!\S)#\w+")
HORIZONTAL_SPACING_RE = re.compile(r"[ \t]{2,}")
EXTRA_NEWLINES_RE = re.compile(r"\n{3,}")
