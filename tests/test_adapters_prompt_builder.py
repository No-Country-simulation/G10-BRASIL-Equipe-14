from src.pipeline.adapters_prompt_builder import (
    build_fix_request,
    build_correction_prompt,
)


def test_build_fix_request_includes_hashtag_limit():
    request = build_fix_request(
        ["6 hashtags (limite 3–5)"],
        "linkedin",
    )

    assert request is not None
    assert "3 e 5" in request


def test_build_fix_request_body_limits():
    request = build_fix_request(
        ["body com 1500 caracteres (limite 1–1200)"],
        "faq",
    )

    assert request is not None
    assert "1 a 1200" in request


def test_build_fix_request_mentions_with_at():
    request = build_fix_request(
        ["menção com @ (usuario): marcaria outra conta"],
        "instagram",
    )

    assert request is not None
    assert "@" in request
    assert 'escreva os nomes sem "@"' in request


def test_build_fix_request_faq_missing_short_response():
    request = build_fix_request(
        ["card de FAQ sem a seção **Resposta curta:**"],
        "faq",
    )

    assert request is not None
    assert "**Resposta curta:**" in request


def test_build_fix_request_review_tag_required():
    request = build_fix_request(
        [
            "FAQ respondido sem resposta aceita na entrada: deveria começar com [PRECISA DE REVISÃO TÉCNICA]"
        ],
        "faq",
    )

    assert request is not None
    assert "[PRECISA DE REVISÃO TÉCNICA]" in request


def test_build_fix_request_empty_errors_returns_none():
    request = build_fix_request([], "linkedin")
    assert request is None


def test_build_correction_prompt_returns_none_when_no_errors():
    result = build_correction_prompt(
        previous_response='{"title": "Valid"}',
        errors=[],
        channel="linkedin",
    )
    assert result is None


def test_build_correction_prompt_returns_tuples_when_errors_exist():
    result = build_correction_prompt(
        previous_response='{"title": "Invalid"}',
        errors=["6 hashtags (limite 1–3)"],
        channel="x/twitter",
    )

    assert result is not None
    system_prompt, user_prompt = result

    assert isinstance(system_prompt, str)
    assert isinstance(user_prompt, str)
    assert "corretor" in system_prompt.lower()
    assert "6 hashtags" in user_prompt
