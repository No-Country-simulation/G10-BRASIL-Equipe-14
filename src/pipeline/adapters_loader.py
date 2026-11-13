from src.config import PROMPTS_ADAPTERS_DIR, CHANNEL_PROMPTS
from src.utils.prompt_reader import load_markdown_prompt


def load_adapter_base_prompt(channel: str) -> str:
    try:
        channel_file = CHANNEL_PROMPTS[channel]
    except KeyError as exc:
        raise ValueError(f"Canal desconhecido: {channel}") from exc

    channel_prompt = load_markdown_prompt(PROMPTS_ADAPTERS_DIR / channel_file)
    if channel in {"faq", "newsletter"}:
        return channel_prompt

    common = load_markdown_prompt(PROMPTS_ADAPTERS_DIR / "common_rules.md")
    return f"{common}\n\n{channel_prompt}"


def get_system_prompt(channel: str) -> str:
    return load_adapter_base_prompt(channel)
