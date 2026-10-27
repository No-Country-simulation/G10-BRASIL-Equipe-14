# Mapeamento de Fontes e Ingestão de Amostra de Dados (Samples)

- **Projeto:** CommunityLab - Motor Inteligente de Transformação e Distribuição para Comunidades Digitais
- **Responsáveis:** Equipe 14 - Turma G10
- **Status:** Aprovado / Em Implementação
- **Versão:** 1.0 (Semana 1)
- **Última Atualização:** 27 de Outubro de 2026

---

## Sumário

- [1. Visão Geral](#1-visão-geral)
- [2. Mapeamento por Fonte](#2-mapeamento-por-fonte)
- [3. Diretrizes Gerais de Coleta](#3-diretrizes-gerais-de-coleta)
- [4. Guia de Execução e Validação](#4-guia-de-execução-e-validação-passo-a-passo)

---

## 1. Visão Geral
Este documento especifica os parâmetros operacionais, regras de requisição, cabeçalhos de identificação ética e rotinas de coleta implementadas em script Python para as três fontes de dados públicas consideradas pelo CommunityLab.

---

## 2. Mapeamento por Fonte

### 2.1. Stack Exchange API
* **Endpoint Base:** `[https://api.stackexchange.com/2.3/questions](https://api.stackexchange.com/2.3/questions)`
* **Código Python:** `src/pipeline/sample_collector.py`
* **Módulo Python:** `DataSourceCollector.fetch_stack_exchange()`
* **Método HTTP:** `GET`
* **Parâmetros de Consulta:**
  * `site`: `stackoverflow`
  * `order`: `desc`
  * `sort`: `votes`
  * `tagged`: Definido como `artificial-intelligence` via `DEFAULT_TAG` em `src/config.py`.
  * `pagesize`: `10` (configurado via DEFAULT_LIMIT)
  * `fromdate`: Timestamp Unix fixo de corte temporal (`1761027120`)
  * `filter`: `default`

* **Cabeçalho HTTP:**
  * `User-Agent`: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36` (configurado via `HEADERS` em `src/config.py`)
  * `Accept-Encoding`: `gzip, deflate` (requerido pela API para descompressão automática e definido via `HEADERS` em `src/config.py`)

---

### 2.2. Hacker News (via Algolia API)
* **Endpoint Base:** `[https://hn.algolia.com/api/v1/search_by_date](https://hn.algolia.com/api/v1/search_by_date)`
* **Código Python:** `src/pipeline/sample_collector.py`
* **Módulo Python:** `DataSourceCollector.fetch_hacker_news()`
* **Método HTTP:** `GET`
* **Parâmetros de Consulta:**
  * `query`: Definido como `artificial-intelligence` via `DEFAULT_TAG` em `src/config.py`
  * `tags`: `story`
  * `hitsPerPage`: `10` (configurado via DEFAULT_LIMIT)
  * `numericFilters`: Filtro temporal dinâmico por timestamp de criação (`created_at_i>=1761027120`)

* **Cabeçalho HTTP:**
  * `User-Agent`: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36` (configurado via `HEADERS` em `src/config.py`)

---

### 2.3. Mastodon API
* **Endpoint Base:** `https://{instance}/api/v1/timelines/tag/{hashtag}`
* **Instância:** `mastodon.social`
* **Hashtag:** Definido como `artificial-intelligence` via `DEFAULT_TAG` em `src/config.py`
* **Código Python:** `src/pipeline/sample_collector.py`
* **Módulo Python:** `DataSourceCollector.fetch_mastodon()`
* **Método:** `GET`
* **Parâmetros de Consulta:**
  * `limit`: `10` (configurado via DEFAULT_LIMIT)
* **Cabeçalho HTTP:**
  * `User-Agent`: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36` (configurado via `HEADERS` em `src/config.py`)

* **Regras de Tratamento de Dados:**

    Foco na recuperação cronológica reversa dos posts mais recentes da timeline pública por hashtag na instância alvo (`mastodon.social`), preservando o payload bruto integral sem forçar filtros de timestamp incompatíveis com a rota básica.

---

## 3. Diretrizes Gerais de Coleta
1. **Isolamento de Erros:** Exceções capturadas na coleta de uma fonte específica registram o erro via logging sem interromper o fluxo das demais fontes.


2. **Persistência de Samples:** Falha na coleta de uma fonte não deve abortar o pipeline das demais fontes.
3. **Persistência de Samples:** Os samples obtidos diretamente das APIs são gravados localmente na pasta `data/samples/` utilizando convenção de nomenclatura sem sublinhados na fonte:

  * sample_stackexchange_api.json
  * sample_hackernews_api.json
  * sample_mastodon_api.json

---

## 4. Guia de Execução e Validação (Passo a Passo)
Siga os passos abaixo para configurar o ambiente local via uv, executar o script modular de coleta e rodar a suite de testes automatizados com pytest e mocks.

#### Passo 1: Estrutura de Diretórios e Pacotes
Garanta que a árvore de pastas e os ficheiros de inicialização (`__init__.py`) respeitam o isolamento modular:

```markdown
projeto/
├── data/
│   └── samples/                     # Destino dos arquivos gerados pelo coletor
├── src/
│   ├── __init__.py
│   ├── config.py                    # Centraliza URLs, parâmetros globais e headers
│   └── pipeline/
│       ├── __init__.py
│       └── sample_collector.py      # Classe DataSourceCollector modularizada
        └──run_sample_collector.py   # Script central de execução
├── tests/
│   └── test_sample_collector.py     # Suite de testes unitários

```

#### Passo 2: Executando a Coleta Integrada
Execute o script de execução do pipeline de ingestão dos samples:

```python
uv python -m src.pipeline.run_sample_collector
```

* **Comportamento esperado:** O script consultará sequencialmente as APIs do Stack Exchange, Hacker News e Mastodon e salvará os respetivos ficheiros em `data/samples/`.

#### Passo 3: Executando os Testes Automatizados
Para validar o comportamento dos coletores e assegurar a integridade estrutural das respostas simuladas, execute a suite de testes através do `pytest`:

```bash
uv run pytest

```

Se desejar executar um teste unitário específico para uma fonte:

```bash
uv run pytest tests/test_sample_collector.py -k "test_fetch_stack_exchange_raw"

```

- **Comportamento esperado:** Todos os testes unitários cobrindo as três fontes devem retornar sucesso (`PASSED`).