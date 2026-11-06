---
prompt_id: router
issue: "#8 [S1-03] Desenvolver Prompt do Router"
versao: 0.4
autor: Gustavo/Equipe 14 G10
modelo_alvo: Gemini free tier (gemini-3.5-flash-lite ou gemini-3.1-flash-lite) | Groq | Ollama
temperatura: 0.0
formato_saida: JSON (responseMimeType="application/json" no Gemini; response_format={"type":"json_object"} no Groq)
entrada: 1 thread (pergunta/post + respostas) no formato data/schemas/input_schema.json
atualizado em: 04/11/2026
---

# Sistema de Roteamento e Classificação LLM (Router Prompt)

## 1. Visão Geral e Arquitetura

O sistema adota uma arquitetura modular e desacoplada em Python, separando a lógica de configuração, clientes de API, prompts, pipeline de execução e regras de validação.

```text
thread (input_schema) ──► LLM Router (Pipeline) ──► JSON de classificação ──► Nó IF/Switch no n8n ──► adapter (LinkedIn / FAQ / Newsletter), moderação ou descarte
```

### 1.1. Estrutura de Pastas

```text
.
├── 📁 data/
│   └── 📁 prompts/
│       ├── 📄 system.md               # Define a persona central do Router e diretrizes de saída em JSON
│       ├── 📄 evaluation_rubric.md    # Contém os critérios analíticos de cálculo do relevance_score em 4 passos
│       ├── 📄 few_shot_examples.md    # Exemplos práticos modelados (conquistas, dúvidas, ruídos) para calibração
│       └── 📄 guardrails.md           # Regras rígidas de segurança contra prompt injection e tratamento de links
├── 📁 src/
│   ├── 📄 config.py                   # Centraliza variáveis de ambiente, caminhos e temperatura padrão.
│   ├── 📁 utils/
│   │   ├── 📄 prompt_loader.py        # Carrega e monta dinamicamente o system prompt a partir dos arquivos md
│   │   ├── 📄 json_parser.py          # Realiza o parse seguro e extração de blocos JSON das respostas da LLM
│   │   └── 📄 http_client.py          # Gerencia requisições HTTP e conexões padronizadas com as APIs
│   ├── 📁 services/
│   │   ├── 📄 llm_service.py          # Implementa as funções específicas de chamada por API (call_gemini, call_groq)
│   │   └── 📄 llm_providers.py        # Dicionário de Registro (LLM_PROVIDERS) e fachada unificada call_llm
│   ├── 📁 pipeline/
│   │   └── 📄 eval_router.py          # Orquestrador principal da pipeline, medição de latência e CLI de testes
│   └── 📁 validation/
│       └── 📄 rules_validator.py     # Validador de schema, consistência e regras de negócio/scores esperados
└── 📁 tests/
    └── 📄 test_rules_validator.py    # Suíte de testes unitários automatizados via pytest para as regras de validação
```

### 1.2. Decisão de Arquitetura: Princípio da Responsabilidade Única (SRP) e Modularidade
Adoção de arquitetura orientada à Responsabilidade Única (Single Responsibility Principle - SRP). Cada módulo do diretório `src/` e `data/` possui um papel estrito e bem delimitado na aplicação:

1. **Gestão de Prompts Desacoplada (`data/prompts/` e `src/utils/prompt_loader.py`):**
   Instruções de sistema, rubricas de pontuação, exemplos *few-shot* e *guardrails* de segurança residem em arquivos Markdown individuais. O `prompt_loader.py` é o único responsável por carregar, concatenar e versionar essas partes dinamicamente.

2. **Camada de Utilitários (`src/utils/`):**
   * `http_client.py`: Centraliza a infraestrutura de rede e o tratamento de conexões HTTP.
   * `prompt_loader.py:` Carrega e une os blocos de prompt dinamicamente.
   * `json_parser.py`: Trata a higienização de Markdown e tratamento de erros de parsing do JSON retornado pelas LLMs.

3. **Isolamento de Provedores e Fachada de LLM (`src/services/`):**
   * `llm_service.py`: Contém exclusivamente a lógica de integração de baixo nível com as APIs externas das LLMs selecionadas.
   * `llm_providers.py`: Atua como uma fachada unificada através de um *Registry Pattern* (`LLM_PROVIDERS`), permitindo que a pipeline chame qualquer LLM de forma transparente via `call_llm(provider, system, user)`, abstraindo chaves, URLs e formatos de payload.

4. **Orquestração e Validação do Pipeline (`src/pipeline/eval_router.py` e `src/validation/rules_validator.py`):**
   * `eval_router.py`: orquestra o ciclo de vida do benchmark: leitura das entradas, disparo das requisições via fachada, cronometragem da latência (`time.perf_counter`), consolidação dos resultados e salvamento de relatórios.
   * `rules_validation.py`: Contém estritamente as regras determinísticas de checagem do schema e consistência dos scores/rotas contra os casos de teste esperados.

5. **Testes Unitários (`tests/tests_rule_validator.py`)

   * `tests_rule_validator.py`: Contém os testes unitários para validar se as regras estão sendo validadas corretamente (schema, tipos, faixas de score e rotas sugeridas) utilizando o pytest para garantir 100% de conformidade com as regras de negócio.

Essa divisão garante facilidade na escrita de testes unitários (via `pytest`), previne acoplamentos circulares de importação e simplifica a inclusão futura de novos provedores sem a necessidade de modificar o fluxo do roteador.

---

## 3. Configurações (`src/config.py`) e Variáveis de Ambiente

O arquivo `src/config.py` centraliza a inicialização do ambiente (`python-dotenv` a partir da raiz) e define as constantes globais:

- **PROJECT_ROOT:** Caminho raiz do projeto.

- **DEFAULT_TEMPERATURE:** Fixada em 0.0 para garantir comportamento determinístico e evitar alucinações estruturais nas classificações.

- **PROMPT_ENUM:** Enum dos prompts e schemas configurados para chamada no arquivo `src/validation/rules_validator.py`.

- **Provedores e Modelos:**
   - **{LLM}_MODEL** e **LLM_API_URL:** Configurados para extrair as informações do arquivo `.env`. Para cada LLM adicionada, foi adotado o padrão de adicionar essas mesmas variáveis, somente alterando o nome do modelo a ser utilizado (Por ora, GEMINI e GROQ). 
   - **{LLM}_API_KEY:** Chaves de API obtidas diretamente do arquivo `.env`.

---

## 4. Regras de Negócio e Roteamento

- O LLM **classifica** cada thread (tipo, sentimento, tema, score) e **sugere** uma rota.

- O n8n recalcula a rota com as regras determinísticas. Se o modelo errar só a rota, o nó condicional corrige.

- A regra "≥ 3 conquistas na semana → Resumo Semanal" não é decidida pelo LLM: é uma agregação do lote feita no n8n/DuckDB contando os itens com `type = job_achievement`.

- **Uma chamada = uma thread.** Se o registro de entrada trouxer várias perguntas diferentes em `interactions`, o n8n precisa separar previamente uma pergunta por chamada.

---

## 5. Organização dos Prompts (`data/prompts/`)

Para manter o código limpo e modular, o **system prompt** foi dividido em arquivos de texto específicos carregados dinamicamente por `prompt_loader.py`:

- **system.md:** Define a persona central do Router do CommunityLab e as instruções fundamentais de saída estrita em JSON.

- **evaluation_rubric.md:** Contém o detalhamento analítico do cálculo do relevance_score em 4 passos e os critérios para definição de tipos (type) e pontuações.

- **few_shot_examples.md:** Casos de exemplo modelados (conquistas, dúvidas com resposta, ruídos e frustrações) para calibrar modelos que necessitem de suporte a formato.

- **guardrails.md:** Diretrizes rígidas de segurança contra prompt injection, tratamento de HTML/links, proibição de invenção de fatos, além de uma camada de proteção e mascaramento de PII (dados pessoais) e senhas expostas nas threads.


---

## 6. Fluxo de Execução do Pipeline (`src/pipeline/eval_router.py`)

- **Entrada:** Carrega os casos de teste reais (`router_real_cases.json`) ou sintéticos (`router_synthetic_cases.json`).
 
- **Validação Inicial:** Executa `rules_validation.py` para garantir que o formato de entrada está íntegro.

- **Seleção de Provedor:** Permite alternar via CLI (`--provider gemini` ou `--provider groq`).

- **Chamada LLM:** O router dispara a requisição utilizando a fachada call_llm mapeada no registro de provedores (`llm_providers.py`).

- **Verificação de latência:** Mede o tempo de execução de cada thread utilizando `time.perf_counter()`.

- **Validação de Saída:** O `rules_validation.py` compara o JSON retornado com o esperado.

- **Persistência:** Grava os relatórios detalhados com latência, acurácia e metadados na pasta `/docs/reports/`.

---

## 7. Avaliação e Execução do Benchmark

```bash
# Exemplos de uso na raiz do repositório:
uv run python -m src.pipeline.eval_router                         # Executa usando Gemini por padrão
uv run python -m src.pipeline.eval_router --provider groq         # Executa usando Groq
uv run python -m src.pipeline.eval_router --dry-run               # Testa a pipeline sem disparar APIs
uv run python -m src.pipeline.eval_router --only real_se          # Filtra a execução pelos casos reais do Stack Exchange
uv run python -m src.pipeline.eval_router --replay src/validation/cases/router_casos_reais.json # Executa somente os casos com dados reais
uv run python -m src.pipeline.eval_router --replay src/validation/cases/router_casos_sinteticos.json # Executa somente os casos com dados sinteticos
uv run python -m src.pipeline.eval_router --replay src/validation/outputs/<arquivo>.json # Reavalia saídas já salvas, sem chamar API
uv run python -m src.pipeline.eval_router --cases src/validation/cases/router_cases_reais.json --only <case name> # Rodar cases específicos

```

>[!ATTENTION]
>Critério de aceite: 100% dos casos aprovados.

---

## Changelog

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
