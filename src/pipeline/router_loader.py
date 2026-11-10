from src.config import PROMPTS_ROUTER
from src.utils.prompt_reader import load_markdown_prompt


def load_prompt_files(*file_names: str) -> str:
    contents = [
        load_markdown_prompt(PROMPTS_ROUTER / file_name) for file_name in file_names
    ]

    return "\n\n".join(contents)


def load_router_base_prompt() -> str:
    return load_prompt_files(
        "system.md",
        "evaluation_rubric.md",
        "guardrails.md",
    )


def load_router_few_shot_prompt() -> str:
    return load_prompt_files("few_shot_examples.md")
