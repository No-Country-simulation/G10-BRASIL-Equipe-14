from __future__ import annotations

from src.pipeline.router_prompt_builder import (
    build_user_prompt,
    build_correction_prompt,
)


def test_build_user_prompt():
    case = {"input": {"id": "thread_01", "content": "Exemplo de conteúdo"}}
    prompt = build_user_prompt(case)

    assert "Classifique a thread abaixo:" in prompt
    assert "THREAD:" in prompt
    assert '"id": "thread_01"' in prompt
    assert '"content": "Exemplo de conteúdo"' in prompt


def test_build_correction_prompt():
    previous_response = '{"invalid": true}'
    errors = ["Campo 'topic' ausente", "Valor de relevância inválido"]

    system_prompt, user_prompt = build_correction_prompt(
        previous_response=previous_response, errors=errors
    )

    assert "Você é um corretor de saída JSON" in system_prompt
    assert previous_response in user_prompt
    assert "- Campo 'topic' ausente" in user_prompt
    assert "- Valor de relevância inválido" in user_prompt