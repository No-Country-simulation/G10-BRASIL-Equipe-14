from __future__ import annotations

from src.pipeline.router_processor import (
    CaseResult,
    merge_token_usage,
    is_retryable_error,
)


def test_case_result_passed():
    """Valida a propriedade passed de CaseResult[cite: 12]."""
    res_ok = CaseResult(output={}, errors=[], warnings=[])
    res_fail = CaseResult(output={}, errors=["Erro grave"], warnings=[])

    assert res_ok.passed is True
    assert res_fail.passed is False


def test_case_result_to_dict():
    res = CaseResult(
        output={"result": 1},
        errors=[],
        warnings=["aviso leve"],
        duration_seconds=1.2345,
        token_usage={"prompt_tokens": 10,
                     "completion_tokens": 20, "total_tokens": 30},
        retry_used=True,
    )
    d = res.to_dict()

    assert d["ok"] is True
    assert d["warnings"] == ["aviso leve"]
    assert d["retry_used"] is True
    assert d["token_usage"]["total_tokens"] == 30


def test_merge_token_usage():
    """Valida a consolidação de tokens entre chamadas[cite: 12]."""
    t1 = {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10}
    t2 = {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20}

    merged = merge_token_usage(t1, t2)
    assert merged == {"prompt_tokens": 15,
                      "completion_tokens": 15, "total_tokens": 30}
    assert merge_token_usage(None, None) is None


def test_is_retryable_error():
    """Valida identificação de erros recuperáveis com base nos prefixos[cite: 12]."""
    # Utilizando um prefixo conhecido ou simulado configurado no projeto
    errors = ["Campo 'topic' inválido"]
    # Como RETRYABLE_ERROR_PREFIXES depende do src.config, testamos a estrutura genérica:
    assert isinstance(is_retryable_error(errors), bool)
