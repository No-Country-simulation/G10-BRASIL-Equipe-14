---
Prompt_id: router
Issue: "#8 [S1-03] Desenvolver Prompt do Router"
Versão: 0.4.1
Autor: Equipe 14 G10 (Gustavo/Vitor)
Modelo: Gemini free tier (gemini-3.5-flash-lite ou gemini-3.1-flash-lite) | Groq
Temperatura: 1.0 nos modelos Gemini 3 (recomendação do Google); 0.0 nos demais
Entrada: 1 thread (pergunta/post + respostas) no formato data/schemas/input_schema.json
Formato_saida: JSON (responseMimeType="application/json" no Gemini; response_format={"type":"json_object"} no Groq)
Atualizado em: 09/11/2026
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
   - [3.1. Configurações Principais](#31-configurações-principais)
   - [3.2. Provedores e Modelos](#32-provedores-e-modelos)
- [4. Contrato de Dados e Validação de Schema](#4-contratos-de-dados-e-validação-de-schema)
   - [4.1. Validação de Entrada](#41-validação-de-entrada)
   - [4.2. Contrato de Saída](#42-contrato-de-saída)
- [5. Regras de Negócio e Roteamento](#5-regras-de-negócio-e-roteamento)
- [6. Organização dos Prompts](#6-organização-dos-prompts)
   - [6.1. System Prompts](#61-system-prompts)
   - [6.2. Correção da Resposta](#62-correção-da-resposta)
- [7. Fluxo de Execução do Pipeline](#7-fluxo-de-execução-do-pipeline)
   - [7.1. Pipeline](#71-pipeline)
   - [7.2. Métricas](#72-métricas)
- [8. Execução e Avaliação do Benchmark](#8-execução-e-avaliação-do-benchmark)
- [9. Resultados do Benchmark](#9-resultados-do-benchmark)
   - [9.1. Execução do Teste 01 (09/11/2026)](#91-execução-de-teste-01-09112026)
   - [9.2. Execução do Teste 02 (10/11/2026)](#92-execução-de-teste-02-10112026)
- [10.Changelog](#10-changelog)

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
│       │     ├── 📄 evaluation_rubric.md          # Contém os critérios analíticos de cálculo do relevance_score
│       │     ├── 📄 few_shot_examples.md          # Exemplos práticos modelados para calibração
│       │     └── 📄 guardrails.md                 # Regras de segurança contra prompt injection e proteção de PII
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
│   │   ├── 📄 llm_service.py                      # Implementa as funções específicas de chamada por API
│   │   └── 📄 llm_providers.py                    # Dicionário de Registro e fachada unificada call_llm
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

A arquitetura atual separa configuração da execução, composição dos prompts, processamento dos casos, integração com provedores, validação determinística e geração de relatórios.

O `eval_router.py`é o ponto de entrada do benchmark, enquanto as responsabilidades são distribuídas entre `router_setup.py`, `router_processor.py` e `router_report.py`.

>[!TIP]
>A decisão arquitetural, suas motivações, alternativas e consequências estão documentadas no [ADR-004 — Arquitetura do Sistema de Roteamento e Classificação LLM](../adr/004-arquitetura-router.md).

---

## 3. Configurações e Variáveis de Ambiente

O arquivo `src/config.py` centraliza caminhos, modelos, temperaturas, URLs e chaves utilizadas pelo pipeline.

### 3.1. Configurações Principais

- `PROJECT_ROOT`: raiz do projeto.
- `DEFAULT_CASES`: arquivos de casos utilizados por padrão.
- `OUTPUTS_DIR`: diretório dos relatórios gerados.
- `ROUTER_VERSION`: versão do prompt e do benchmark.
- `GEMINI_MODEL` e `GROQ_MODEL`: modelos utilizados pelos provedores.
- `GEMINI_TEMPERATURE`: temperatura aplicada ao Gemini.
- `DEFAULT_TEMPERATURE`: temperatura padrão dos demais provedores.
- `GEMINI_API_KEY` e `GROQ_API_KEY`: chaves carregadas por meio de arquivo de variável de ambiente `.env`.

>[!WARNING]
>As chaves de API não devem ser incluídas em código, casos de teste, relatórios ou arquivos versionados.

### 3.2. Provedores e Modelos

O Router foi configurado com os seguintes provedores:

- `gemini`;
- `groq`.

A seleção ocorre pela opção:

```bash
--provider gemini
--provider groq
```

A fachada `call_llm` normaliza a resposta dos provedores em uma estrutura
comum contendo:

- Texto retornado;
- Tokens de entrada;
- Tokens de conclusão;
- Tokens totais.

Com essa estrutura é possível adicionar ou remover modelos de forma simplificada e centralizada.

---

## 4. Contratos de Dados e Validação de Schema

O Router recebe uma thread por chamada, conforme o `data/schemas/input_schema.json`.

A entrada contém:

- `id`;
- `source`;
- `url`;
- `interactions`.

A primeira interação representa o post original. As demais representam respostas ou comentários.

### 4.1. Validação de entrada

O `router_setup.py` valida os casos antes da execução usando `invalid_inputs()` do `router_validator.py`. Casos incompatíveis com o schema impedem o início do benchmark.

### 4.2. Contrato de saída

A resposta do modelo deve ser um objeto JSON contendo exatamente os campos definidos pelo contrato de saída:

- `id`;
- `source`;
- `type`;
- `sentiment`;
- `topic_category`;
- `topics`;
- `original_language`;
- `has_answer`;
- `relevance_score`;
- `suggested_route`;
- `summary`;
- `justification`.

O `router_validator.py` rejeita:

- Campos ausentes;
- Campos adicionais;
- Tipos inválidos;
- Valores fora dos enums;
- `topics` vazio, com mais de três itens ou com itens não textuais;
- `relevance_score` fora do intervalo de 0 a 100;
- `summary` com mais de 200 caracteres;
- Inconsistências em `has_answer`;
- Rotas incompatíveis com as regras determinísticas.

`has_answer` só pode ser `true` quando uma interação posterior possuir `raw_metadata.is_accepted = true`.

---

## 5. Regras de Negócio e Roteamento

- O LLM **classifica** cada thread (tipo, sentimento, tema, score) e **sugere** uma rota.

- O n8n recalcula a rota com as regras determinísticas. Se o modelo errar só a rota, o nó condicional pode corrigir.

- A regra "≥ 3 conquistas na semana → Resumo Semanal" não é decidida pelo LLM: é uma agregação do lote feita no n8n/DuckDB contando os itens com `type = job_achievement`.

- **Uma chamada = uma thread.** Se o registro de entrada trouxer várias perguntas diferentes em `interactions`, o n8n precisa separar previamente uma pergunta por chamada.

---

## 6. Organização dos Prompts

### 6.1. System Prompts

Os prompts do Router são mantidos em arquivos Markdown independentes dentro de `data/prompts/router/`:

- `system.md`: define o papel do Router, as instruções gerais e o contrato de saída;
- `evaluation_rubric.md`: define tipos, sentimentos, cálculo de relevância e regras de roteamento;
- `guardrails.md`: define proteção contra prompt injection, PII, credenciais, segredos e saídas fora do contrato;
- `few_shot_examples.md`: contém exemplos de referência usados para corrigir respostas inválidas.

O `router_loader.py` carrega o prompt base com:

- `system.md`;
- `evaluation_rubric.md`;
- `guardrails.md`.

Os exemplos de `few_shot_examples.md` são carregados separadamente e incluídos somente quando a primeira resposta apresentar erro de formato ou de rótulo. Essa estratégia reduz os tokens de entrada nas chamadas que já produzem uma resposta válida.

### 6.2. Correção da Resposta

Quando necessário, o `router_processor.py`:

1. Preserva a resposta anterior;
2. Envia os erros encontrados ao modelo;
3. Inclui os exemplos *few-shot*;
4. Solicita somente um novo JSON válido;
5. Faz o parsing e a validação novamente;
6. Soma os tokens e a duração das chamadas realizadas.

---

## 7. Fluxo de Execução do Pipeline

### 7.1. Pipeline

1. **Entrada:** o `router_setup.py` interpreta os argumentos da CLI; 
2. **Carregamento dos casos:** São carregados os casos reais ou sintéticos a partir de:
  - `data/prompts/cases/router_cases_reais.json`
  - `data/prompts/cases/router_cases_sinteticos.json`
3. **Validação inicial:** o `router_setup.py` verifica se os casos de entrada são compatíveis com o schema de entrada, utilizando `invalid_inputs()` do `router_validator.py`;
4. **Preparação da execução:** o `router_setup.py` carrega o prompt base  e os exemplos *few-shot* separadamente;
5. **Definição dos provedores:** O provedor, modelo, temperatura e modo de execução são definidos;
6. **Execução dos casos:** O `eval_router.py` percorre os casos e delega o processamento individual ao `router_processor.py`;
7. **Chamada LLM:** O `router_processor.py` chama `call_llm(provider, system, user)`. A fachada localiza o provedor no registro `LLM_PROVIDERS`, recupera a API Key correspondente e delega a chamada para `call_gemini` ou `call_groq`:
   - Chama o provedor em execução normal
   - Gera uma saída simulada em `dry-run`
   - Reutiliza uma saída existente em `replay`
8. **Parsing da resposta:** O `router_processor.py` utiliza o `json_parser.py` para interpretar o JSON retornado pelo provedor;

9. **Validação de saída:** o `router_processor.py` utiliza o `router_validator.py` para verificar o JSON retornado em relação ao schema, às regras de negócio e aos valores esperados do caso;
10. **Fallback:** Se houver erro de formato ou rótulo, o processador faz uma nova chamada com os exemplos *few-shot* e revalida a resposta;
11. **Medição de latência e tokens:** o `router_processor.py` mede a duração de cada chamada utilizando `time.perf_counter()` e registra os tokens de entrada, saída e totais quando o provedor disponibiliza essas métricas;
12. **Relatório:** o `router_report.py` exibe os resultados individuais e consolida as métricas;
13. **Persistência:** o `router_report.py` salva os resultados, metadados, acurácia, latência e uso de tokens em `data/prompts/outputs/` nas execuções reais.

### 7.2. Métricas

O relatório registra:

- Duração por caso;
- Duração média;
- Duração total;
- Tokens de entrada;
- Tokens de saída;
- Tokens totais;
- Quantidade de retries, quando registrada;
- Acurácia da execução.

Em `dry-run`, os tokens são informados como indisponíveis. Em `replay`, também são indisponíveis quando o arquivo reutilizado não contém métricas de uso.

---

## 8. Execução e Avaliação do Benchmark

Os comandos devem ser executados na raiz do repositório:

```bash
# Execução padrão com Gemini
uv run python -m src.pipeline.eval_router

# Execução com Groq
uv run python -m src.pipeline.eval_router --provider groq

# Execução sem chamadas à API
uv run python -m src.pipeline.eval_router --dry-run

# Execução filtrada por nome de caso
uv run python -m src.pipeline.eval_router --only real_se

# Execução dos casos reais
uv run python -m src.pipeline.eval_router --cases data/prompts/cases/router_cases_reais.json --tag reais

# Execução dos casos sintéticos
uv run python -m src.pipeline.eval_router --cases data/prompts/cases/router_cases_sinteticos.json --tag sinteticos

# Execução filtrada por fonte ou identificador
uv run python -m src.pipeline.eval_router --cases data/prompts/cases/router_cases_reais.json --only mastodon

# Reavaliação de saídas de casos reais previamente salvos
uv run python -m src.pipeline.eval_router --cases data/prompts/cases/router_cases_reais.json --replay data/prompts/outputs/<arquivo>.json

# Reavaliação de saídas de casos sintéticos previamente salvos
uv run python -m src.pipeline.eval_router --cases data/prompts/cases/router_cases_sinteticos.json --replay data/prompts/outputs/<arquivo>.json
```

- **Modos de execução:**
   - **Execução normal:** chama o provedor selecionado e salva o relatório.
   - `dry-run`: não chama APIs, usa saídas simuladas e não mede tokens reais.
   - `replay`: reutiliza saídas previamente salvas e não realiza novas chamadas. O arquivo de casos ainda é carregado separadamente; informe `--cases` para avaliar apenas o conjunto correspondente ao replay.

A opção `--sleep` controla o intervalo entre casos em execução normal. Em casos que exigem retry, a chamada adicional também deve respeitar o limite do provedor.

O relatório salvo contém os resultados dos casos, a acurácia, a latência e o uso consolidado de tokens quando essas métricas estiverem disponíveis.

---

## 9. Resultados do Benchmark
- **Configurações:** gemini-3.5-flash-lite, temperatura 1.0
- **Execução:** 09/11/2026 e 10/11/2026 (2 Rodadas de Teste) 
- **Casos:** 32 casos (17 reais e 15 sintéticos) 
- **Versão:** 0.4.1

### 9.1. Execução de Teste 01 (09/11/2026)
| Conjunto         | Acerto | Percentual | Tempo de Execução | Tempo Médio por Requisição | Tokens Consolidados (Entrada) | Tokens Consolidados (Saída) | Tokens Consolidados (Total) | Tokens Consolidados (Média) |
|:-----------------|:-------|:-----------|:------------------|:----------|:----------|:----------|:----------|:--------|
| Dados Reais      | 17/17  | 100%       | 48.18s            | 2.83s     | 76.101    | 3.674     | 79.775    |4.693    |
| Dados Sintéticos | 15/15  | 100%       | 46.19s            | 3.08s     | 42.716    | 2.509     | 45.225    |3.015    |

**Saídas do modelo:** `data/prompts/outputs/router_v0.4.1_gemini_reais_20261109-1100.json` e `data/prompts/outputs/router_v0.4.1_gemini_sinteticos_20261109-1207.json`.

### 9.2. Execução de Teste 02 (10/11/2026)
| Conjunto         | Acerto | Percentual | Tempo de Execução | Tempo Médio por Requisição | Tokens Consolidados (Entrada) | Tokens Consolidados (Saída) | Tokens Consolidados (Total) | Tokens Consolidados (Média) |
|:-----------------|:-------|:-----------|:------------------|:----------|:----------|:----------|:----------|:--------|
| Dados Reais      | 17/17  | 100%       | 186.24s            | 10.96s     | 76.110    | 3.599    | 79.709    |4.689    |
| Dados Sintéticos | 15/15  | 100%       | 124.61s            | 8.31s     | 47.508    | 2.685     | 50.193    |3.347    |

**Saídas do modelo:** `data/prompts/outputs/router_v0.4.1_gemini_reais_20261110-1211.json` e `data/prompts/outputs/router_v0.4.1_gemini_sinteticos_20261110-1203.json`.

### 9.3. Conclusão

Os testes atenderam com êxito ao critério de aceite do benchmark, alcançando **100% de aprovação** nos casos esperados.

Durante o Teste 02, foram identificadas requisições com status HTTP 503, possivelmente relacionadas à limitação ou à instabilidade do provedor, tanto no conjunto de dados reais quanto no sintético. Essas ocorrências, entretanto, não impediram a conclusão das execuções.

No caso CT32 (`pii_secret_exposto`), verificou-se uma anomalia por conta do retry na segunda rodada de teste. O CT32 mais que dobrou o consumo de tokens, partindo de **3.111 tokens** e **sem retry** no teste 01 (09/11) para **8.066 tokens** e **com retry** no teste 02 (10/11). 

As definições do retry no `router_processor.py` foram ajustadas para evitar que o prompt inteiro fosse carregado novamente a cada retry. Com esse ajuste, em duas execuções isoladas, o CT32 consumiu um total de **3556 tokens** e **3205 tokens**, respectivamente.

**Avisos**
- Em um caso, a rota sugerida pelo modelo diferiu da rota definida pelas regras, que podem ser ajustadas no n8n:
   * CT32 (`pii_secret_exposto`): modelo sugeriu 'moderation', as regras dão 'discard' (o n8n corrige)

>[!TIP]
>Os resultados detalhados das execuções do Router estão documentados em [docs/benchmarks](../benchmarks/).


---

## 10. Changelog

### 0.4.1 (09/11/2026) — Revisão, Modularização e Instrumentação do Router
- **Documentação e arquitetura:**
  - Separação da decisão arquitetural em um ADR específico: `docs/adr/004-arquitetura-router.md`.
  - Atualização da especificação para refletir os módulos `router_setup.py`, `router_processor.py` e `router_report.py`.
  - Separação dos resultados detalhados do benchmark em documento próprio: `docs/benchmarks/router-benchmark-results.md`.
  - Uso condicional de `few_shot_examples.md` somente em tentativas de correção.

- **Prompts do Router:**
  - Revisão do `system.md`, mantendo o papel do Router, o formato de entrada e o schema de saída.
  - Revisão do `evaluation_rubric.md`, alinhando as regras de tipos, `has_answer`, sentimento, relevância e roteamento.
  - Revisão do `few_shot_examples.md`, preservando exemplos de referência para calibração.
  - Revisão do `guardrails.md`, reforçando o contrato JSON estrito, a proteção contra prompt injection e o tratamento de PII e segredos.
  - Ajuste da composição dos prompts modulares para reduzir redundâncias.

- **Casos de avaliação:**
  - Revisão dos casos reais das fontes Stack Overflow/Stack Exchange, Mastodon e Hacker News.
  - Manutenção apenas de casos reais sustentados pelos samples disponíveis no projeto.
  - Adição de 1 casos real de Mastodon, abrangendo uma opinião negativa e 2 casos reais do Hacker News, abrangendo uma propaganda e um post somente com título, sem conteúdo.
  - Adição de 3 casos sintéticos do Hacker News, abrangendo relato de sucesso, tentativa de jailbreak e exposição de PII/segredo fictício.
  - O conjunto real passou a totalizar 17 casos: 10 de Stack Overflow/Stack Exchange, 5 de Mastodon e 2 de Hacker News.
  - O conjunto sintético passou a totalizar 15 casos: 2 de Stack Overflow/Stack Exchange, 10 de Mastodon e 3 de Hacker News.

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
