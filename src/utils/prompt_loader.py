from src.config import PROMPTS_DIR


def load_router_system_prompt() -> tuple[str, str]:
    system_text = (PROMPTS_DIR / "system.md").read_text(encoding="utf-8")
    rubric_text = (PROMPTS_DIR / "evaluation_rubric.md").read_text(encoding="utf-8")
    guardrails_text = (PROMPTS_DIR / "guardrails.md").read_text(encoding="utf-8")
    examples_text = (PROMPTS_DIR / "few_shot_examples.md").read_text(encoding="utf-8")

    combined_prompt = f"""
    {system_text}
    
    {rubric_text}
    
    {guardrails_text}
    
    {examples_text}
    """
    return combined_prompt.strip()
