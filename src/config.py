# Configuração de diretórios relativos

from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROMPTS_DIR = DATA_DIR / "prompts"
PROCESSED_DIR = DATA_DIR / "processed"
SAMPLES_DIR = DATA_DIR / "samples"
SCHEMA_DIR = DATA_DIR / "schemas"
INPUT_SCHEMA_PATH = SCHEMA_DIR / "input_schema.json"
