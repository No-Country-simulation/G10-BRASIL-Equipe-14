import time
from typing import Any
import requests
from src.config import (
    DEFAULT_TIMEOUT_SECONDS,
    MAX_RETRY_WAIT_SECONDS,
    RETRY_BACKOFF_SECONDS,
    RETRYABLE_STATUS_CODES,
)


def _retry_wait(response: requests.Response, attempt: int) -> int:
    retry_after = response.headers.get("Retry-After")

    if retry_after is not None:
        try:
            return min(max(int(retry_after), 0), MAX_RETRY_WAIT_SECONDS)
        except ValueError:
            pass

    return min(RETRY_BACKOFF_SECONDS * (2**attempt), MAX_RETRY_WAIT_SECONDS)


def http_post(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    retries: int = 3,
) -> dict[str, Any]:
    request_headers = {
        "Content-Type": "application/json",
        **headers,
    }

    for attempt in range(retries + 1):
        try:
            response = requests.post(
                url,
                json=payload,
                headers=request_headers,
                timeout=DEFAULT_TIMEOUT_SECONDS,
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError as exc:
                    raise RuntimeError(
                        "O provedor retornou uma resposta " "que não é JSON válido."
                    ) from exc

                if not isinstance(data, dict):
                    raise RuntimeError(
                        "O provedor retornou um JSON que não é um objeto."
                    )

                return data

            if response.status_code in RETRYABLE_STATUS_CODES and attempt < retries:
                wait = _retry_wait(response, attempt)
                print(
                    f"  HTTP {response.status_code} na tentativa "
                    f"{attempt + 1}/{retries + 1}: limite ou instabilidade "
                    f"no provedor; aguardando {wait}s antes da tentativa "
                    f"{attempt + 2}/{retries + 1}..."
                )
                time.sleep(wait)
                continue

            raise RuntimeError(
                f"HTTP {response.status_code}: " "o provedor recusou a requisição."
            )

        except requests.exceptions.RequestException as exc:
            if attempt < retries:
                wait = min(
                    RETRY_BACKOFF_SECONDS * (2**attempt),
                    MAX_RETRY_WAIT_SECONDS,
                )
                print(
                    f"  Erro de rede: aguardando {wait}s "
                    f"para nova tentativa ({attempt + 2}/{retries + 1})..."
                )
                time.sleep(wait)
                continue

            raise RuntimeError(f"Falha de conexão com a API: {exc}") from exc

    raise RuntimeError(
        "Sem resposta da API após esgotar as tentativas de retry.")
