from pathlib import Path


def load_markdown_prompt(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo de prompt não encontrado: {file_path}")

    return file_path.read_text(encoding="utf-8").strip()
