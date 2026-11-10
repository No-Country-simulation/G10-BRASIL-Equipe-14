---
prompt_id: router
issue: "#8 [S1-03] Desenvolver Prompt do Router"
versao: 0.4.1
autor: Gustavo/Equipe 14 G10
modelo_alvo: Gemini free tier (gemini-3.5-flash-lite ou gemini-3.1-flash-lite) | Groq
temperatura: 1.0 nos modelos Gemini 3 (recomendação do Google); 0.0 nos demais
formato_saida: JSON (responseMimeType="application/json" no Gemini; response_format={"type":"json_object"} no Groq)
entrada: 1 thread (pergunta/post + respostas) no formato data/schemas/input_schema.json
atualizado em: 09/11/2026
---

# Sistema de Roteamento e Classificação LLM (Router Prompt)

O Sistema de Roteamento e Classificação (Router Prompt) é o componente central responsável por analisar threads de conteúdo (compostas por um post original e suas respectivas interações), aplicar inferência controlada via LLM e determinar a rota editorial ou operacional adequada.

---

## Sumário

- [1. Objetivo](#1-objetivo)
- [2. Visão Geral e Arquitetura](#2-visão-geral-e-arquitetura)
   - [2.1. Estrutura de Pastas](#21-estrutura-de-pastas)
   - [2.2. Decisão de Arquitetura](#22-decisão-de-arquitetura)
- [3. Configurações e Variáveis de Ambiente](#3-configurações-e-variáveis-de-ambiente)
- [4. Contrato de Dados e Validação de Schema](#4-contratos-de-dados-e-validação-de-schema)
- [5. Regras de Negócio e Roteamento](#5-regras-de-negócio-e-roteamento)
- [6. Organização dos Prompts](#6-organização-dos-prompts)
- [7. Fluxo de Execução do Pipeline](#7-fluxo-de-execução-do-pipeline)
- [8. Execução e Avaliação do Benchmark](#8-execução-e-avaliação-do-benchmark)
- [9. Resultados](#9-resultados)
   - [9.1. Resumo Executivo](#91-resumo-executivo)
   - [9.2. Casos Reais por Fonte de Dados](#92-casos-reais-por-fonte-de-dados)
   - [9.3. Casos Sintéticos por Fonte de Dados](#93-casos-sintéticos-por-fonte-de-dados)
   - [9.4. Resultado dos Casos Executados](#94-resultado-dos-casos-executados)

---

## 1. Objetivo

O Router tem como objetivo processar uma thread contendo o post original e suas interações, realizando a classificação estruturada do conteúdo em conformidade estrita com o schema de saída. A resposta gerada é validada deterministicamente para assegurar a integridade do payload antes do encaminhamento para as etapas subsequentes do pipeline editorial ou operacional.

---

## 2. Visão Geral e Arquitetura

O sistema adota uma arquitetura modular e desacoplada em Python, separando a lógica de configuração, clientes de API, prompts, pipeline de execução e regras de validação.

```text
thread (input_schema) ──► LLM Router (Pipeline) ──► JSON de classificação ──► Nó IF/Switch no n8n ──► adapter (LinkedIn / FAQ / Newsletter), moderação ou descarte
```

### 2.1. Estrutura de Pastas

```text
.
├── 📁 data/
│   └── 📁 prompts/
│       ├── 📁 router/
│       │     ├── 📄 system.md                     # Define a persona central do Router e diretrizes de saída em JSON
│       │     ├── 📄 evaluation_rubric.md          # Contém os critérios analíticos de cálculo do relevance_score em 4 passos
│       │     ├── 📄 few_shot_examples.md          # Exemplos práticos modelados (conquistas, dúvidas, ruídos) para calibração
│       │     └── 📄 guardrails.md                 # Regras rígidas de segurança contra prompt injection e tratamento de links
│       │
│       ├── 📁 cases/
│       │    ├── 📄 router_cases_reais.json        # Define o case real
│       │    └── 📄 router_cases_sinteticos.json   # Define o case sintetico
│       └── 📁 outputs/                            # Armazenas as saídas consolidadas dos testes executados
│            
├── 📁 src/
│   ├── 📄 config.py                               # Centraliza variáveis de ambiente, caminhos e temperatura padrão.
│   ├── 📁 pipeline/
│   │   ├── 📄 eval_router.py                      # Ponto de entrada e orquestrador do benchmark
│   │   ├── 📄 router_loader.py                    # Carrega e compõe o system prompt modular
│   │   ├── 📄 router_processor.py                 # Executa os casos, faz parsing, validação e mede tokens e latência
│   │   ├── 📄 router_setup.py                     # Define os argumentos da CLI e prepara o contexto de execução
│   │   └── 📄 router_report.py                    # Exibe resultados, consolida métricas e salva os relatórios
│   │ 
│   ├── 📁 services/
│   │   ├── 📄 llm_service.py                      # Implementa as funções específicas de chamada por API (call_gemini, call_groq)
│   │   └── 📄 llm_providers.py                    # Dicionário de Registro (LLM_PROVIDERS) e fachada unificada call_llm
│   ├── 📁 utils/
│   │   ├── 📄 prompt_reader.py                    # Faz a leitura dos arquivos markdown dos prompts
│   │   ├── 📄 cases_loader.py                     # Carrega os arquivos de casos e replay
│   │   ├── 📄 json_parser.py                      # Realiza o parse seguro e extração de blocos JSON das respostas da LLM
│   │   └── 📄 http_client.py                      # Gerencia requisições HTTP e conexões padronizadas com as APIs
│   └── 📁 validation/
│       └── 📄 router_validator.py                 # Validador de schema, consistência e regras de negócio/scores esperados
└── 📁 tests/
    └── 📄 test_router_validator.py                # Suíte de testes unitários automatizados via pytest para as regras de validação
```

### 2.2. Decisão de Arquitetura
Adoção de arquitetura orientada à Responsabilidade Única (Single Responsibility Principle - SRP). Cada módulo do diretório `src/` e `data/` possui um papel estrito e bem delimitado na aplicação:

1. **Gestão de prompts (`data/prompts/router` e `src/pipeline/router_loader.py`)**

   - Os prompts de sistema, as regras de avaliação, os exemplos *few-shot* e os *guardrails* residem em arquivos Markdown independentes.

   - O `router_loader.py` carrega e concatena esses arquivos para formar o prompt utilizado pelo Router.

2. **Camada de utilitários (`src/utils/`)**
   * `http_client.py`: Centraliza a infraestrutura de rede e o tratamento de conexões HTTP.
   * `json_parser.py`: Interpreta as respostas JSON retornadas pelos provedores LLM.
   * `prompt_reader.py`: Realiza a leitura dos arquivos markdown.
   * `cases_loader.py`: Realiza o carregamentos dos arquivos de casos e de replay.

3. **Isolamento de Provedores e Serviços de LLM (`src/services/`):**
   - `llm_service.py`: Contém a lógica de baixo nível para chamadas às APIs do Gemini e do Groq.
   - `llm_providers.py`: fornece o registro de provedores e a fachada `call_llm`, associando cada provedor à sua função e à sua API Key carregada de `src/config.py`. A fachada `call_llm` centraliza a seleção do provedor, mas não contém regras de classificação nem de validação. Essas responsabilidades permanecem no pipeline e no `router_validator.py`.
   - `eval_router.py`: seleciona o provedor pela opção `--provider` e chama `call_llm`, mantendo a escolha da implementação fora da lógica do benchmark.

4. **Orquestração e Validação do Pipeline (`src/pipeline/`):**

   * `router_setup.py`: Define os argumentos da linha de comando, carrega e filtra os casos, carrega arquivos de replay e prepara o contexto de execução, incluindo provedor, modelo e temperatura.

   * `router_processor.py`: Executa cada caso em modo normal, `dry-run` ou `replay`; monta o prompt de entrada, chama o provedor LLM, interpreta a resposta JSON, mede a duração e registra o uso de tokens quando disponível.

   * `router_report.py`: Exibe os resultados individuais e o resumo da execução, consolida acurácia, latência e tokens e salva o relatório JSON do benchmark.

   * `eval_router.py`: Atua como ponto de entrada e orquestrador do benchmark, conectando a configuração da CLI, o processamento dos casos e a geração do relatório.

   * `router_validator.py`: Aplica as regras determinísticas de validação do schema, dos campos obrigatórios, dos enums, dos scores, de `has_answer` e das rotas esperadas.

5. **Testes Unitários (`tests/test_router_validator.py`):**

   * `test_router_validator.py`: Contém os testes das regras de validação, incluindo tipos, campos obrigatórios, enums, faixas de score, rotas e rejeição de campos adicionais.


Essa divisão facilita a escrita de testes, evita acoplamentos desnecessários e permite adicionar novos provedores sem alterar as regras de classificação.

---

## 3. Configurações e Variáveis de Ambiente

O arquivo `src/config.py` centraliza a inicialização do ambiente e define as constantes globais:

- **`PROJECT_ROOT`:** caminho raiz do projeto.
- **`GEMINI_TEMPERATURE`:** temperatura utilizada nas chamadas Gemini (`1.0` por padrão).
- **`DEFAULT_TEMPERATURE`:** temperatura padrão utilizada pelos demais provedores, atualmente `0.0`.
- **`PROMPT_ENUMS`:** conjunto de valores permitidos para os campos de saída, utilizado pelo `router_validator.py`.

### Provedores e modelos

- **`{LLM}_MODEL` e `{LLM}_API_URL`:** modelo e URL configurados para cada provedor.
- **`{LLM}_API_KEY`:** chaves de API obtidas a partir do arquivo `.env`.
- Os provedores atualmente integrados ao pipeline são Gemini e Groq.

---

## 4. Contratos de Dados e Validação de Schema

A integridade do pipeline depende de duas barreiras contratuais implementadas em JSON Schema:

- **Schema de Entrada (input_schema.json):** Valida o payload recebido (post original, metadados, lista de interações e timestamps) antes de enviá-lo para processamento. Rejeita payloads que não contenham as chaves obrigatórias (como id, source, interactions).

- **Schema de Saída (output_schema.json):** Valida o objeto retornado pela LLM. Assegura que os campos de classificação, pontuação de confiança e rota editorial estejam dentro dos tipos de dados e enumerations (enums) esperados pelo sistema downstream (ex: n8n).

---

## 5. Regras de Negócio e Roteamento

- O LLM **classifica** cada thread (tipo, sentimento, tema, score) e **sugere** uma rota.

- O n8n recalcula a rota com as regras determinísticas. Se o modelo errar só a rota, o nó condicional corrige.

- A regra "≥ 3 conquistas na semana → Resumo Semanal" não é decidida pelo LLM: é uma agregação do lote feita no n8n/DuckDB contando os itens com `type = job_achievement`.

- **Uma chamada = uma thread.** Se o registro de entrada trouxer várias perguntas diferentes em `interactions`, o n8n precisa separar previamente uma pergunta por chamada.

---

## 6. Organização dos Prompts

O *system prompt* é dividido em arquivos específicos carregados dinamicamente pelo `router_loader.py`:

- **`system.md`:** define o papel do Router, o formato de entrada e o schema de saída.
- **`evaluation_rubric.md`:** define os critérios de classificação, cálculo do `relevance_score` e escolha das rotas.
- **`few_shot_examples.md`:** contém exemplos de conquistas, dúvidas, ruídos e frustrações para calibrar o formato e as regras.
- **`guardrails.md`:** define as regras de segurança contra *prompt injection*, tratamento de HTML e links, proteção de PII e contrato estrito de saída JSON.

---

## 7. Fluxo de Execução do Pipeline

- **Entrada:** o `router_setup.py` define os argumentos da execução e carrega os casos reais ou sintéticos a partir de:
  - `data/prompts/cases/router_cases_reais.json`;
  - `data/prompts/cases/router_cases_sinteticos.json`.

- **Validação inicial:** o `router_setup.py` verifica se os casos de entrada são compatíveis com o schema esperado, utilizando `invalid_inputs()` do `router_validator.py`.

- **Preparação da execução:** o `router_setup.py` carrega o system prompt, prepara o contexto de execução, seleciona o provedor e configura o modelo, a temperatura e o modo de execução.

- **Seleção do provedor:** permite alternar entre Gemini e Groq usando `--provider gemini` ou `--provider groq`.

- **Execução dos casos:** o `eval_router.py` percorre os casos e delega o processamento individual ao `router_processor.py`.

- **Chamada LLM:** o `router_processor.py` chama `call_llm(provider, system, user)`. A fachada localiza o provedor no registro `LLM_PROVIDERS`, recupera a API Key correspondente e delega a chamada para `call_gemini` ou `call_groq`.

- **Parsing da resposta:** o `router_processor.py` utiliza o `json_parser.py` para interpretar o JSON retornado pelo provedor.

- **Medição de latência e tokens:** o `router_processor.py` mede a duração de cada chamada utilizando `time.perf_counter()` e registra os tokens de entrada, saída e totais quando o provedor disponibiliza essas métricas.

- **Validação de saída:** o `router_processor.py` utiliza o `router_validator.py` para verificar o JSON retornado em relação ao schema, às regras de negócio e aos valores esperados do caso.

- **Modos sem chamada à API:**
  - `dry-run` gera uma saída simulada para validar o fluxo;
  - `replay` reutiliza saídas previamente salvas;
  - nesses modos, os tokens são informados como indisponíveis quando não existem métricas armazenadas.

- **Relatório:** o `router_report.py` exibe os resultados individuais, a taxa de acerto, a latência média e os tokens consolidados.

- **Persistência:** o `router_report.py` salva os resultados, metadados, acurácia, latência e uso de tokens em `data/prompts/outputs/` nas execuções reais.

---

## 8. Execução e Avaliação do Benchmark

Os comandos devem ser executados na raiz do repositório:

```bash
# Executa os casos usando Gemini por padrão
uv run python -m src.pipeline.eval_router

# Executa os casos usando Groq
uv run python -m src.pipeline.eval_router --provider groq

# Executa a pipeline sem realizar chamadas às APIs
# O valor de Tokens será apresentado como indisponível
uv run python -m src.pipeline.eval_router --dry-run

# Executa somente casos cujo nome contém "real_se"
uv run python -m src.pipeline.eval_router --only real_se

# Executa todos os casos reais
uv run python -m src.pipeline.eval_router --cases data/prompts/cases/router_cases_reais.json

# Executa todos os casos sintéticos
uv run python -m src.pipeline.eval_router --cases data/prompts/cases/router_cases_sinteticos.json

# Executa somente casos reais cujo nome contém "mastodon"
uv run python -m src.pipeline.eval_router --cases data/prompts/cases/router_cases_reais.json --only mastodon

# Reavalia saídas já salvas, sem chamar a API
# Tokens: indisponível se o replay não contiver métricas de uso
uv run python -m src.pipeline.eval_router --replay data/prompts/outputs/<arquivo>.json
```

## 9. Resultados
>**Configurações:** gemini-3.5-flash-lite, temperatura 1.0
>**Execução:** 09/11/2026 | 32 casos (17 reais e 15 sintéticos) | Versão: 0.4.1

### 9.1. Resumo Executivo:

| Conjunto         | Acerto | Percentual | Tempo de Execução | Tempo Médio por Requisição |
|:-----------------|:-------|:-----------|:------------------|:------------------|
| Dados Reais      | 13/17  | 72%        | 52.81s            | 2.93s             |
| Dados Sintéticos | 15/15  | 100%       | 22.66s            | 1.89s             |


### 9.2. Casos Reais por Fonte de Dados:

| Fonte	                         | Casos  | Tipos  |
|:-------------------------------|:-------|:-------|
| Stack Overflow/Stack Exchange	 |  10    | perguntas técnicas, respostas aceitas e score |
| Mastodon	                     |   5    | ruído, opinião, idioma e sentimento           |
| Hacker News	                   |   2    | propaganda, debates e análises textuais       |
| **Total**	                         |  **17**    |  |

### 9.3. Casos Sintéticos por Fonte de Dados:

| Fonte	                         | Casos  | Tipos  |
|:-------------------------------|:-------|:-------|
| Stack Overflow/Stack Exchange	 |   2    | perguntas técnicas, resposta aceita e pergunta sem resposta |
| Mastodon	                     |  10    | conquistas, depoimento, dúvidas, feedback de curso, debate, ruído, prompt injection e certificação           |
| Hacker News	                   |   3    | relato de sucesso, jailbreak e exposição de PII/secret      |
| **Total**	                     |  **15**    |  |

### 9.4. Resultado dos Casos Executados

| Conjunto         | Fonte de Dados                | Case                     | Acerto | Tempo de Execução |
|:-----------------|:------------------------------|:-------------------------|:-------|:------------------|
| Dados Reais      | Stack Overflow/Stack Exchange | real_se_duvida_com_resposta_aceita_llamaindex | Ok | 2.26s |
| Dados Reais      | Stack Overflow/Stack Exchange | real_se_duvida_com_resposta_aceita_vscode |  Ok     | 1.83s |
| Dados Reais      | Stack Overflow/Stack Exchange | real_se_duvida_com_resposta_aceita_symfony_ai | Ok     | 1.85s|
| Dados Reais      | Stack Overflow/Stack Exchange | real_se_resposta_nao_aceita_windsurf |Ok     | 2.01s |
| Dados Reais      | Stack Overflow/Stack Exchange | real_se_duvida_sem_resposta_muito_vista | Ok     | 2.39s   |
| Dados Reais      | Stack Overflow/Stack Exchange | real_se_duvida_sem_resposta_langchain_mcp | Ok     | 1.95s  |
| Dados Reais      | Stack Overflow/Stack Exchange | real_se_limitacao_de_ferramenta_tom_objetivo | Ok     | 1.89s  |
| Dados Reais      | Stack Overflow/Stack Exchange | real_se_desanimo_pessoal_vibe_coder |  Ok     | 2.01s       |
| Dados Reais      | Stack Overflow/Stack Exchange | real_se_debate_mercado_com_respostas |  Ok     | 1.94s    |
| Dados Reais      | Stack Overflow/Stack Exchange | real_se_pergunta_vaga_ruido |  Falha     | 2.02s     |
| Dados Reais      | Mastodon | real_mastodon_bot_politica | Ok     | 1.86s        |
| Dados Reais      | Mastodon | real_mastodon_noticia_ia_rss | Ok     | 1.91s         |
| Dados Reais      | Mastodon | real_mastodon_opiniao_com_link | Ok     | 19.33s    |
| Dados Reais      | Mastodon | real_mastodon_japones_metadado_errado | Ok     | 1.97s  |
| Dados Reais      | Mastodon | real_mastodon_opiniao_negativa | Ok     | 1.92s  |
| Dados Reais      | Hacker News | real_hn_propaganda    | Ok     | 1.84s            |
| Dados Reais      | Hacker News | real_hn_sem_conteudo    | Ok     | 1.84s            |
| Dados Sintéticos | Sintético (Mastodon) | conquista_vaga_detalhada  |   OK   | 1.86s             |
| Dados Sintéticos | Sintético (Mastodon)  | conquista_vaga_ingles     |   OK   | 1.97s             |
| Dados Sintéticos | Sintético (Mastodon)  | depoimento_generico       |   OK   | 1.82s             |
| Dados Sintéticos | Sintético (Stack Overflow/Stack Exchange)  | duvida_com_resposta_aceita|   OK   | 1.87s             |
| Dados Sintéticos | Sintético (Stack Overflow/Stack Exchange) | duvida_sem_resposta       |   OK   | 2.06s             |
| Dados Sintéticos | Sintético (Mastodon)  | duvida_frustrada          |   OK   | 1.84s             |
| Dados Sintéticos | Sintético (Mastodon)   | feedback_negativo_curso   |   OK   | 1.81s             |
| Dados Sintéticos | Sintético (Mastodon)  | spam                      |   OK   | 1.81s             |
| Dados Sintéticos | Sintético (Mastodon)   | so_emoji                  |   OK   | 1.76s             |
| Dados Sintéticos | Sintético (Mastodon)   | prompt_injection          |   OK   | 1.95s             |
| Dados Sintéticos | Sintético (Mastodon)   | debate                    |   OK   | 1.92s             |
| Dados Sintéticos | Sintético (Mastodon)   | certificacao              |   OK   | 1.99s             |
| Dados Sintéticos | Sintético (Hacker News)   | relato_sucesso      |   OK   | 1.99s             |
| Dados Sintéticos | Sintético (Hacker News)   | jailbreaking           |   OK   | 1.99s             |
| Dados Sintéticos | Sintético (Hacker News)   | pii_secret_exposto      |   OK   | 1.99s             |



>[!ATTENTION]
>Critério de aceite: 100% dos casos aprovados.

---

## Changelog

### 0.4.1 (09/11/2026) — Revisão, Modularização e Instrumentação do Router
- **Prompts do Router:**
  - Revisão do `system.md`, mantendo o papel do Router, o formato de entrada e o schema de saída.
  - Revisão do `evaluation_rubric.md`, alinhando as regras de tipos, `has_answer`, sentimento, relevância e roteamento.
  - Revisão do `few_shot_examples.md`, preservando exemplos de referência para calibração.
  - Revisão do `guardrails.md`, reforçando o contrato JSON estrito, a proteção contra prompt injection e o tratamento de PII e segredos.
  - Ajuste da composição dos prompts modulares para reduzir redundâncias.

- **Casos de avaliação:**
  - Revisão dos casos reais das fontes Stack Overflow/Stack Exchange, Mastodon e Hacker News.
  - Manutenção apenas de casos reais sustentados pelos samples disponíveis no projeto.
  - O conjunto real passou a totalizar 17 casos: 10 de Stack Overflow/Stack Exchange, 5 de Mastodon e 2 de Hacker News.
  - Adição de 3 casos sintéticos do Hacker News, abrangendo relato de sucesso, tentativa de jailbreak e exposição de PII/segredo fictício.

- **Validação do Router:**
  - Ajuste da validação para rejeitar campos adicionais no JSON de saída.
  - Confirmação da validação de objetos JSON, campos obrigatórios, enums e faixa de `relevance_score`.
  - Validação determinística de `has_answer` e `suggested_route`.

- **Modularização do pipeline:**
  - Refatoração do `eval_router.py` para reduzir responsabilidades e manter apenas a orquestração do benchmark.
  - Criação do `router_setup.py` para configuração da CLI, carregamento dos casos, preparação do prompt e seleção do provedor.
  - Criação do `router_processor.py` para execução dos casos, parsing, validação, medição de latência e captura do uso de tokens.
  - Criação do `router_report.py` para exibição dos resultados, consolidação das métricas e persistência dos relatórios.

- **Métricas e modos de execução:**
  - Inclusão do uso de tokens de entrada, saída e total nas respostas dos provedores.
  - Exibição e persistência das métricas de tokens por caso e de forma consolidada nas execuções reais.
  - Tratamento explícito de tokens indisponíveis em `dry-run` e `replay` sem métricas armazenadas.
  - Registro da latência individual, do tempo médio e do tempo total da execução.

- **Cobertura dos casos:**
  - Mantida a cobertura de respostas aceitas e não aceitas, perguntas sem resposta, conteúdo vago, feeds RSS, opiniões autorais, idioma inconsistente, sentimento negativo, prompt injection e exposição de dados sensíveis fictícios.

### 0.4.0 (04/11/2026) — Refatoração Modular, Separação de Prompts e Expansão para Hacker News
- **Arquitetura & Clean Code:**
  - Refatoração completa do `eval_router.py` aplicando o **Princípio da Responsabilidade Única (SRP)**: a orquestração do pipeline, o carregamento de prompts, a parsing de JSON e as regras de validação foram desacoplados em módulos dedicados.
  - Criação da camada de serviços (`src/services/`) com o padrão **Registry / Fachada** (`llm_providers.py`) e implementações isoladas para cada provedor em `llm_service.py`.
  - Adição de medição e registro de **latência por requisição** com `time.perf_counter()`, incluindo média e tempo total no relatório final de saída.
  - Ajuste e padronização do carregamento primordial de variáveis de ambiente no topo de `src/config.py` via `python-dotenv`.
- **Modularização do System Prompt (`data/prompts/`):**
  - O System Prompt monolítico foi fracionado em arquivos `.md` independentes: `system.md` (persona/output), `evaluation_rubric.md` (regras e 4 passos do score), `few_shot_examples.md` (exemplos modelados) e `guardrails.md` (segurança/injection).
  - Implementação do `prompt_loader.py` para composição dinâmica do prompt antes das chamadas.
- **Suíte de Casos de Teste & Novas Fontes:**
  - Adição oficial do **Hacker News (HN)** como terceira fonte monitorada (junto ao Stack Overflow / Stack Exchange e Mastodon).
  - Reestruturação e padronização dos casos reais em 15 casos equilibrados (5 SO, 5 Mastodon, 5 HN) e 12 casos sintéticos, cobrindo todo o espectro de rotas e schemas.


### 0.3.1 (24/10/2026), compatível com o `input_schema.json` do merge da PR #54
- A entrada passa a ter `url` no topo e `title` separado de `content`; as fontes agora são Stack Overflow/Stack Exchange, Mastodon e Hacker News (Bluesky saiu do enum).
- Casos de teste e exemplos atualizados para o schema novo: casos sintéticos de Bluesky viraram Mastodon e ganharam uma `url` de exemplo.
- As regras de classificação não mudaram em relação à 0.3.0.

### 0.3.0 (24/10/2026), após a 1ª rodada real no Gemini (gemini-3.5-flash-lite)
Rodada da v0.2: 12/12 nos sintéticos e 10/14 nos reais. Ajustes para os 4 erros:
- **`has_answer` só com resposta aceita.** O modelo já tratava resposta não aceita como "sem resposta" (caso Windsurf). A regra ficou estrita e determinística, e o FAQ só nasce de solução confirmada. Esperado do caso Windsurf atualizado para newsletter_only.
- **`negative` sem "insegurança pessoal".** Pedido de conselho em tom construtivo é neutral; só desistência declarada vai para moderação. O modelo leu o caso "vibe coder" como neutral, que era a alternativa já anotada na revisão. Esperado atualizado.
- **Pergunta vaga virou um passo separado.** O modelo pulava o critério de 20–39 e punha todas as dúvidas sem resposta em 45.
- **Link com comentário próprio é debate, não noise.** O modelo descartou a opinião do professor no Mastodon.
- **Posição dentro da faixa com números** (meio da faixa, até +10 por engajamento, até +5 por IA/dados/cloud). Na rodada, todas as dúvidas sem resposta receberam 45, com 147 ou 1.373 visualizações.
- **Temperatura 1.0 nos modelos Gemini 3**, como recomenda o guia do Google.

### 0.2.0 (21/10/2026), após simulação com 14 itens reais (10 do Stack Exchange, 4 do Mastodon) e os 12 casos sintéticos
- **Uma thread por chamada**, e `type`/`sentiment` passam a se referir ao post original (antes, as respostas podiam mudar o sentimento).
- **`has_answer` definido com regra objetiva.** `is_answered = true` sem o texto da resposta passa a contar como `false`: o arquivo atual do Stack Exchange não traz as respostas.
- **Score em 2 passos (faixa → posição).** O bônus de IA/dados/cloud não tira mais o item da faixa. Na v0.1, como toda a amostra do Stack Exchange tem a tag `artificial-intelligence`, o +10 inflava tudo e fazia dúvidas sem resposta passarem de 59.
- **Engajamento alto com número:** view_count ≥ 1000 ou score ≥ 10.
- **Moderação antes do corte por score.** Na v0.1, uma reclamação curta (score < 40) era descartada antes de chegar à regra de moderação.
- **Definições ajustadas:** `negative` cobre desânimo pessoal; limitação de ferramenta em tom objetivo é `neutral`; `debate` inclui pedido de conselho; nova categoria `dev_tools` (IDEs e assistentes de código, muito presentes nos dados reais).
- **Mastodon:** notícia repassada por bot/RSS sem comentário da pessoa vira `noise`, e `original_language` passa a vir do texto (na amostra real, um post em japonês veio com `language: "en"`).
- Exemplo 4 (frustração → moderação) e `justification` citando faixa e regra, para facilitar a revisão. Os exemplos não repetem os casos de teste, para não "vazar" a resposta caso alguém os inclua no prompt.

### 0.1.0 (21/10/2026)
- Rascunho inicial, sem teste em modelo.
