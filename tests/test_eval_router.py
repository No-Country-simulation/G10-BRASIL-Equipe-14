from __future__ import annotations

import json
from unittest.mock import patch

from src.pipeline import eval_router


@patch("src.pipeline.router_setup.invalid_inputs", return_value=[])
def test_eval_router_dry_run_end_to_end(mock_invalid_inputs, tmp_path):
    """Valida o teste de ponta a ponta do router em modo dry-run utilizando arquivos temporários."""
    # 1. Cria um arquivo de casos simulado minimalista
    case_file = tmp_path / "router_cases_test.json"
    cases_data = [
        {
            "case": "test_case_01",
            "input": {
                "id": "t1",
                "source": "stackoverflow",
                "interactions": [
                    {
                        "author": "dev1",
                        "title": "Como configurar o ambiente",
                        "content": "Dúvida sobre configuração de python e virtualenv.",
                    }
                ],
            },
            "expected": {
                "suggested_route": "discard",
            },
        }
    ]
    case_file.write_text(json.dumps(cases_data), encoding="utf-8")

    # 2. Simula os argumentos de linha de comando apontando para o arquivo de teste e ativando o --dry-run
    test_args = [
        "eval_router.py",
        "--cases",
        str(case_file),
        "--dry-run",
    ]

    with patch("sys.argv", test_args):
        # O dry-run deve processar com sucesso e retornar o código de saída 0 (todos aprovados)
        exit_code = eval_router.main()

        assert exit_code == 0
