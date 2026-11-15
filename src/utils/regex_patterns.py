from datetime import datetime
import re

# Configuração de regex para remover code fences
CODE_FENCE_PATTERN = re.compile(
    r"^\s*```(?:json)?\s*(.*?)\s*```\s*$",
    re.IGNORECASE | re.DOTALL,
)
