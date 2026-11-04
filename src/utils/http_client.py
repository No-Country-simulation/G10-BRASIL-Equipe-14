import time
import requests


def http_post(url: str, payload: dict, headers: dict, retries: int = 3) -> dict:
    request_headers = {"Content-Type": "application/json", **headers}

    for attempt in range(retries + 1):
        try:
            response = requests.post(
                url, json=payload, headers=request_headers, timeout=90
            )

            if response.status_code == 200:
                return response.json()

            if response.status_code in (429, 500, 503) and attempt < retries:
                wait = 15 * (attempt + 1)
                print(
                    f"  HTTP {response.status_code}: limite ou instabilidade no provedor; aguardando {wait}s..."
                )
                time.sleep(wait)
                continue

            error_body = response.text[:300]
            raise RuntimeError(f"HTTP {response.status_code}: {error_body}")

        except requests.exceptions.RequestException as exc:
            if attempt < retries:
                wait = 15 * (attempt + 1)
                print(f"  Erro de rede ({exc}); aguardando {wait}s para retry...")
                time.sleep(wait)
                continue
            raise RuntimeError(f"Falha de conexão com a API: {exc}") from None

    raise RuntimeError("Sem resposta da API após esgotar as tentativas de retry.")
