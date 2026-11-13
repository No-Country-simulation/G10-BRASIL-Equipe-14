---
Issue: "#9 [S1-04] Desenvolver Prompts para as Redes Sociais e #10 [S1-05] Desenvolver Prompts para Newsletter e FAQ Dinâmico"
Versão: 0.4.0
Autor: Equipe 14 G10
Modelo: Gemini free tier (gemini-3.5-flash-lite ou gemini-3.1-flash-lite) | Groq
Temperatura: 1.0 nos modelos Gemini 3 (recomendação do Google); 0.0 nos demais
Entrada: saída do Router (rota success_case ou faq) + item original
Formato_saida: JSON compatível com um item de suggested_content (data/schemas/output_schema.json)
Elaborado em: 13/11/2026

---

# Sistema de Adaptação e Geração de Conteúdo (Adapters)

O Sistema de Adaptação e Geração de Conteúdo é o componente de infraestrutura responsável por consumir as saídas estruturadas do roteador, processar o contexto de threads e interações técnicas, e despachar os jobs para os diferentes canais de destino (redes sociais, newsletters e cards de FAQ). O subsistema garante a execução padronizada de chamadas a provedores LLM, a validação estrita de schemas de entrada e saída, o tratamento resiliente de erros com ciclos de auto-correção e a exportação centralizada de métricas e relatórios analíticos.

---

## Sumário

- [1. Objetivo](#1-objetivo)
- [2. Visão Geral e Arquitetura](#2-visão-geral-e-arquitetura)
   - [2.1. Estrutura de Pastas e Componentes](#21-estrutura-de-pastas)
   - [2.2. Decisão de Arquitetura](#22-decisão-de-arquitetura)
- [3. Configurações e Variáveis de Ambiente](#3-configurações-e-variáveis-de-ambiente)
   - [3.1. Configurações Principais](#31-configurações-principais)
   - [3.2. Provedores e Modelos](#32-provedores-e-modelos)
- [4. Contrato de Dados e Validação de Schema](#4-contratos-de-dados-e-validação-de-schema)
   - [4.1. Validação de Entrada](#41-validação-de-entrada)
   - [4.2. Contrato de Saída](#42-contrato-de-saída)
   - [4.3. Matriz de Critérios de Aceite e Limites por Canal](#43-matriz-de-critérios-de-aceite-e-limites-por-canal)
- [5. Organização dos Prompts e Mecanismos de Autocorreção](#5-organização-dos-prompts-e-mecanismo-de-auto-correção)
   - [5.1. System Prompts e Composição Modular](#51-system-prompts-e-composição-modular)
   - [5.2. Construtor de Prompts e Correção da Resposta](#52-construtor-de-prompts-e-correção-da-resposta)
   - [5.3. Template de Execução no n8n](#53-template-de-execução-no-n8n)
- [6. Fluxo de Execução do Pipeline](#6-fluxo-de-execução-do-pipeline)
   - [6.1. Orquestração do Pipeline](#61-orquestração-do-pipeline)
   - [6.2. Métricas](#62-métricas)
   - [6.3. Saída Agregada ](#63-saída-agregada-para-o-pacote)
- [7. Execução e Avaliação do Benchmark](#7-execução-e-avaliação-do-benchmark)
- [8. Resultados do Benchmark](#8-resultados-do-benchmark)
   - [8.1. Execução do Teste 01](#81-execução-de-teste-01)
   - [8.2. Execução do Teste 02](#82-execução-de-teste-02)
- [9.Changelog](#9-changelog)


---

## 1. Objetivo

A especificação geral do Sistema de Adaptação e Geração de Conteúdo tem como finalidade documentar a infraestrutura de engenharia, os contratos de dados, o pipeline de execução automatizada e os subsistemas de validação e resiliência compartilhados por todos os canais editoriais. O sistema visa garantir a modularidade no processamento de threads técnicas, o tratamento padronizado de chamadas a provedores de LLM, a aplicação de ciclos integrados de auto-correção baseados em erros do validador e a consistência na exportação de métricas e relatórios analíticos em JSON e CSV.

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
│       ├── 📁 adapters/
│       │     ├── 📄 adapter_blog.md               # Prompt system do canal Blog
│       │     ├── 📄 adapter_discord.md            # Prompt system do canal Discord
│       │     ├── 📄 adapter_faq.md                # Prompt system de FAQ
│       │     └── 📄 adapter_instagram.md          # Prompt system do canal Instagram
│       │     └── 📄 adapter_linkedin.md           # Prompt system do canal Linkedin
│       │     └── 📄 adapter_mastodon.md           # Prompt system do canal Mastodon
│       │     └── 📄 adapter_newsletter.md         # Prompt system de Newsletter
│       │     └── 📄 adapter_x_twitter.md          # Prompt system do canal X/Twitter
│       │     └── 📄 common_rules.md               # Prompt system com regras invioláveis dos canais de redes sociais
│       │
│       ├── 📁 cases/
│       │    └── 📄 adapter_cases.json             # Define os casos configurados baseados nos casos de router real e sintético
│       └── 📁 outputs/                            # Armazenas as saídas consolidadas dos testes executados
│            
├── 📁 src/
│   ├── 📄 config.py                               # Centraliza variáveis de ambiente, caminhos e temperatura padrão.
│   ├── 📁 pipeline/
│   │   ├── 📄 eval_adapters.py                    # Ponto de entrada e orquestrador do benchmark
│   │   ├── 📄 adapters_loader.py                  # Carrega e compõe o system prompt modular
│   │   ├── 📄 adapters_processor.py               # Gerencia o ciclo de vida da execução de cada job
│   │   ├── 📄 adapters_prompt_builder.py          # Constrói os prompts de usuário formatados por canal
│   │   ├── 📄 adapters_setup.py                   # Define os argumentos da CLI e prepara o contexto de execução
│   │   └── 📄 adapters_report.py                    # Exibe resultados, consolida métricas e salva os relatórios
│   │ 
│   ├── 📁 services/
│   │   ├── 📄 llm_service.py                      # Implementa as funções específicas de chamada por API
│   │   └── 📄 llm_providers.py                    # Dicionário de Registro e fachada unificada call_llm
│   ├── 📁 utils/
│   │   ├── 📄 cases_loader.py                     # Carrega os arquivos de casos
│   │   ├── 📄 http_client.py                      # Gerencia requisições HTTP e conexões 
│   │   ├── 📄 json_parser.py                      # Realiza o parse seguro e extração de blocos JSON das respostas da LLM
│   │   ├── 📄 prompt_reader.py                    # Faz a leitura dos arquivos markdown dos prompts
│   │   ├── 📄 provider_config.py                  # Centraliza o mapeamento de configurações de cada provedor LLM
│   │   └── 📄 regex_patterns.py                   # Centraliza as expressões regulares
│   └── 📁 validation/
│       └── 📄 adapters_validator.py               # Validador de limites, consistência e regras de negócio/scores esperados
└── 📁 tests/                                      # Suíte de testes unitários automatizados via pytest para as regras de validação
  
```

### 2.2. Decisão de Arquitetura

A arquitetura atual separa configuração da execução, composição dos prompts, processamento dos casos, integração com provedores, validação determinística e geração de relatórios.

O `eval_adapters.py`é o ponto de entrada do benchmark, enquanto as responsabilidades são distribuídas entre `adapters_loader.py`, `adapters_prompt_builder.py`, `adapters_setup.py`, `adapters_processor.py` e `adapters_report.py`.

>[!TIP]
>A decisão arquitetural, suas motivações, alternativas e consequências estão documentadas no [ADR-005 — Arquitetura do Sistema de Adaptação e Geração de Conteúdo](../adr/005-arquitetura-adapters.md).

---

## 3. Configurações e Variáveis de Ambiente

O arquivo `src/config.py` centraliza caminhos, modelos, temperaturas, URLs e chaves utilizadas pelo pipeline.

### 3.1. Configurações Principais

- `PROJECT_ROOT`: raiz do projeto.
- `ADAPTER_CASES`: arquivo de casos utilizados por padrão.
- `OUTPUTS_DIR`: diretório dos relatórios gerados.
- `ADAPTER_SOCIAL_VERSION`: versão do prompt dos adapters dos canais sociais.
- `ADAPTER_NEWSLETTER_FAQ_VERSION`: versão do prompt dos adapters de FAQ e Newsletter.
- `GEMINI_MODEL` e `GROQ_MODEL`: modelos utilizados pelos provedores.
- `GEMINI_TEMPERATURE`: temperatura aplicada ao Gemini.
- `DEFAULT_TEMPERATURE`: temperatura padrão dos demais provedores.
- `GEMINI_API_KEY` e `GROQ_API_KEY`: chaves carregadas por meio de arquivo de variável de ambiente `.env`.

>[!WARNING]
>As chaves de API não devem ser incluídas em código, casos de teste, relatórios ou arquivos versionados.

### 3.2. Provedores e Modelos

O Adapter foi configurado com os seguintes provedores:

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
# 4. Contratos de Dados e Validação de Schema

O pipeline de adapters consome o arquivo de casos estruturado em jobs e itens (`data/cases/adapter_cases.json`), validando a conformidade por meio do `adapters_validator.py`.

### 4.1. Validação de Entrada

O `adapters_setup.py` carrega e valida o arquivo de casos antes da execução utilizando o `cases_loader.py`.

A estrutura de entrada (`adapter_cases.json`) exige:

* `jobs`: Lista contendo os metadados de execução (nome do job, canal de destino, modelo e parâmetros de temperatura).
* `items`: Dicionário contendo os dados brutos das threads e interações originais que servirão de base para a adaptação editorial.

Arquivos de casos incompatíveis com o schema esperado interrompem a execução do benchmark imediatamente.

### 4.2. Contrato de Saída

A resposta gerada pelo modelo LLM deve retornar estritamente um objeto JSON estruturado de acordo com o canal de destino. O `adapters_validator.py` aplica checagens determinísticas para rejeitar saídas que apresentem:

* Campos obrigatórios ausentes ou chaves adicionais não mapeadas;
* Tipos de dados inválidos (ex: strings onde se esperam listas ou booleanos);
* **Estouro de limites por canal:** Textos que ultrapassem o limite estrito de caracteres configurado para a rede social ou canal de FAQ/Newsletter;
* **Restrições editoriais e formatação:**
    * Presença de menções indesejadas com `@` no corpo do texto (nos canais sociais);
    * Contagem de hashtags fora do intervalo permitido (mínimo e máximo por canal);
    * Inconsistências estruturais nos cards de FAQ (ausência das seções obrigatórias como `**Pergunta:**`, `**Resposta curta:**` e `**Fonte:**`);
    * Falta da tag de revisão obrigatória (`[PRECISA DE REVISÃO TÉCNICA]`) em casos complexos ou sem solução clara.

### 4.3. Matriz de Critérios de Aceite e Limites por Canal
 O script de validação do pipeline valida de forma determinística os parâmetros de cada canal de destino com base na seguinte matriz de limites e restrições:

| Canal | Limite de `body` | Hashtags | Emojis |
|:-----:|:----------------:|:--------:|:------:|
| linkedin | 600–1.300 | 3–5 | ≤ 3 |
| x/twitter | ≤ 280 | 1–2 | livre |
| mastodon | ≤ 500 | ≤ 2 | livre |
| instagram | ≤ 2.200 | 5–10 | ≤ 5 |
| discord | ≤ 2.000 | 0–2 | livre |
| faq | ≤ 1.200 | 0 | livre |
| newsletter | ≤ 3.000 | 0 | livre |
| blog | 500–5.000 | 0–5 | livre |

Além dos limites quantitativos da tabela, o validador automatizado também verifica:
* A conformidade do campo target com o enum de canais suportados;
* O recálculo dinâmico do comprimento utilizando len(body) no código;
* A presença de frases proibidas e o bloqueio de menções com o caractere @ (exigindo handles limpos);
* A checagem de linhas de crédito obrigatórias (como no Stack Overflow) e a detecção de alucinações numéricas (números presentes na saída que não constavam na entrada original).

---

## 5. Organização dos Prompts e Mecanismo de Auto-Correção

### 5.1. System Prompts e Composição Modular

Os prompts do sistema de adapters são mantidos em arquivos Markdown independentes dentro de `data/prompts/adapters/`:

* **Prompts por Canal (`adapter_blog.md`, `adapter_faq.md`, `adapter_linkedin.md`, `adapter_instagram.md`, `adapter_discord.md`, `adapter_mastodon.md`, `adapter_x_twitter.md`e `adapter_newsletter.md`):** Definem o papel editorial específico, as diretrizes de tom de voz e o formato de saída exigido para cada plataforma de destino.
* **Regras Comuns (`common_rules.md`):** Contêm diretrizes invioláveis aplicadas aos canais de redes sociais, como controle rigoroso de emojis, proibição de menções indesejadas com `@` e formatação padronizada de hashtags.

O `adapters_loader.py` compõe o prompt de sistema unificado injetando dinamicamente as regras comuns quando o canal alvo pertence à categoria de redes sociais, garantindo isolamento modular para os canais de curadoria e FAQ.

### 5.2. Construtor de Prompts e Correção da Resposta

O `adapters_prompt_builder.py` é o componente responsável por estruturar a mensagem de usuário (contexto da thread, metadados e interações) enviada às LLMs.

Quando o `adapters_validator.py` detecta uma falha de validação (estouro de limite de caracteres, ausência de seções obrigatórias no FAQ, erro de schema ou ausência de tags técnicas), o `adapters_processor.py` aciona o ciclo de auto-correção:

1. Preserva o histórico da resposta anterior e os erros específicos apontados pelo validador;
2. Envia um prompt direcionado de correção ao modelo, detalhando exatamente quais restrições foram violadas;
3. Solicita a reavaliação estrita e a geração de um novo objeto JSON corrigido;
4. Executa novamente o parsing (`json_parser.py`) e a validação estrita;
5. Soma de forma acumulativa o consumo de tokens e a duração total das tentativas realizadas.

### 5.3. Template de Execução no n8n

O fluxo de integração encarregado de orquestrar as chamadas para os adapters pode utilizar um template padronizado para injetar os metadados de classificação e o conteúdo bruto original no corpo da requisição enviada ao modelo:

```text
Gere o conteúdo para o canal indicado.

CLASSIFICAÇÃO:
{{ JSON.stringify($json.classification) }}

ITEM ORIGINAL:
{{ JSON.stringify($json.item) }}

```

FAQ:
```text
Gere o card de FAQ.
CLASSIFICAÇÃO: {{ JSON.stringify($json.classification) }}
ITEM ORIGINAL: {{ JSON.stringify($json.item) }}
```

Newsletter:
```text
Gere a edição da newsletter.
PERÍODO: {{ $json.reference_period }}
ITENS: {{ JSON.stringify($json.items) }}
```

Esses templates garantem que a LLM receba o contexto estruturado gerado pelo **router** (como tipo, sentimento, tópicos e relevância) atrelado às interações originais da comunidade, permitindo a aplicação correta das diretrizes editoriais específicas de cada canal.

>[!NOTE]
>**Limite de contexto (free tier):** se o lote for grande, envie para a Newsletter apenas os 15 itens com maior `relevance_score` e, em cada um, só `summary`, `topics`, `type` e o primeiro `content` truncado em 500 caracteres. Isso evita estourar tokens e o rate limit do Gemini/Groq.

---

## 6. Fluxo de Execução do Pipeline e Relatórios

### 6.1. Orquestração do Pipeline

1. **Entrada:** o `adapters_setup.py` interpreta os argumentos da CLI;
2. **Carregamento dos casos:** Os jobs e itens de teste são carregados a partir do arquivo padrão `data/cases/adapter_cases.json`
3. **Validação inicial:** o `adapters_setup.py` valida se o arquivo de casos é compatível com o schema estrutural de entrada;
4. **Preparação da execução:** O `adapters_loader.py` compõe o System Prompt modular injetando as regras comuns e o prompt específico do canal correspondente;
5. **Definição dos provedores:** O provedor, modelo, temperatura e modo de execução são definidos;
6. **Execução dos jobs:** O `eval_adapters.py` percorre os jobs e delega o processamento individual ao `adapters_processor.py`;
7. **Chamada LLM:** O `adapters_processor.py` chama `call_llm(provider, system, user)`. A fachada localiza o provedor no registro `LLM_PROVIDERS`, recupera a API Key correspondente e delega a chamada para `call_gemini` ou `call_groq`:
* Chama o provedor em execução normal;
* Gera uma saída simulada em `dry-run`;

8. **Parsing da resposta:** O `adapters_processor.py` utiliza o `json_parser.py` para remover cercas de código (*code fences*) e interpretar o JSON retornado pelo provedor;
9. **Validação de saída:** o `adapters_processor.py` utiliza o `adapters_validator.py` para verificar o JSON retornado em relação ao schema, aos limites estritos do canal e às restrições editoriais;
10. **Auto-Correção (Retry):** Se houver falha de validação (estouro de limite, erro de schema ou ausência de seções obrigatórias), o processador faz uma nova chamada direcionada com os erros apontados e revalida a resposta corrigida;
11. **Medição de latência e tokens:** o `adapters_processor.py` mede a duração de cada chamada utilizando `time.perf_counter()` e registra os tokens de entrada, saída e totais quando o provedor disponibiliza essas métricas;
12. **Relatório:** o `adapters_report.py` exibe os resultados individuais no terminal e consolida as métricas do benchmark;
13. **Persistência:** o `adapters_report.py` salva os resultados detalhados, metadados, taxa de sucesso, latência e uso de tokens em formatos JSON e CSV dentro do diretório de saídas (`data/outputs/`).

### 6.2. Métricas

O relatório consolida e registra:

* Duração por job/caso;
* Duração média;
* Duração total de execução;
* Tokens de entrada;
* Tokens de saída;
* Tokens totais;
* Quantidade de retries/auto-correções realizadas;
* Taxa de sucesso e conformidade com os validadores.

Em modo `dry-run`, os tokens são informados como indisponíveis. Em modo `replay`, também são omitidos caso o arquivo reutilizado não contenha métricas de uso pré-gravadas.

### 6.3. Saída Agregada para o Pacote

Além da newsletter, o mesmo lote alimenta o `processing_summary` do `output_schema.json`. Isso pode ser calculado **sem LLM**, direto em DuckDB/Python:

- `total_interactions` = contagem de itens do lote
- `predominant_feeling` = moda de `sentiment`
- `main_topics` = top 3 de `topics`

---

## 7. Execução e Avaliação do Benchmark

Os comandos devem ser executados na raiz do repositório:

```bash
# Execução padrão com Gemini
uv run python -m src.pipeline.eval_adapters

# Execução com Groq
uv run python -m src.pipeline.eval_adapters --provider groq

# Execução sem chamadas à API
uv run python -m src.pipeline.eval_adapters --dry-run

# Execução filtrada por nome de job específico
uv run python -m src.pipeline.eval_adapters --only <job-especifico>

```

- **Modos de execução:**
   - **Execução normal:** chama o provedor selecionado e salva o relatório.
   - `dry-run`: não chama APIs, usa saídas simuladas e não mede tokens reais.

A opção `--sleep` controla o intervalo entre casos em execução normal. Em cenários que acionam o ciclo de auto-correção (retry), a chamada adicional respeita os limites e as políticas de restrição do provedor.

O relatório gerado e persistido consolida os resultados por job, a taxa de sucesso/conformidade, a latência de execução e o uso total de tokens quando essas métricas estiverem disponíveis. As saídas e o resultado da validação ficam em `data/prompts/outputs/adapters_gemini_<timestamp>.json`.

---

## 8. Resultados do Benchmark
- **Configurações:** gemini-3.5-flash-lite, temperatura 1.0
- **Data da Execução:** 12/11/2026 e 13/11/2026 (2 Rodadas de Teste) 
- **Jobs:** 9 Jobs
- **Versão:** 0.4.0

### 8.1. Execução do Teste 01 
- **Data da Execução:** 12/11/2026
- **Período:** 22:24:06 (UTC-3)

| Canais        | Acerto | Percentual | Tempo de Execução | Tempo Médio por Requisição | Tokens Consolidados (Entrada) | Tokens Consolidados (Saída) | Tokens Consolidados (Total) | Tokens Consolidados (Média) |
|:-----------------|:-------|:-----------|:------------------|:----------|:----------|:----------|:----------|:--------|
| Social/FAQ/Newsletter  | 9/9  | 100%       | 26.02s            | 2.89s     | 20.043    | 2.342     | 22.385    |2.488   |

**Saídas do modelo:** `data/prompts/outputs/adapters_gemini_20261112-2224.json`.

### 8.2. Execução do Teste 02 
- **Data da Execução:** 13/11/2026
- **Período:** 10:39:15 (UTC-3)

| Canais        | Acerto | Percentual | Tempo de Execução | Tempo Médio por Requisição | Tokens Consolidados (Entrada) | Tokens Consolidados (Saída) | Tokens Consolidados (Total) | Tokens Consolidados (Média) |
|:-----------------|:-------|:-----------|:------------------|:----------|:----------|:----------|:---------|:--------|
| Social/FAQ/Newsletter  | 9/9  | 100%       | 22.60s        | 2.51s     | 19.517   | 1.964     | 21.481    |2.387   |

**Saídas do modelo:** `data/prompts/outputs/adapters_gemini_20261113-1039.json`.

### 8.3. Conclusão

As execuções finais do benchmark atenderam com êxito aos critérios de aceite do sistema, alcançando **100% de aprovação (9/9 jobs)** em ambas as rodadas de teste com o modelo `gemini-3.5-flash-lite`.

Durante o ciclo de validação e refinamento que antecedeu a consolidação da versão `0.4.0` dos adapters de faq/newsletter e social, observou-se:

* **Resiliência a Instabilidades de API:** Foram registradas instabilidades pontuais com retornos HTTP 503 do provedor, contornadas com sucesso pelo cliente HTTP resiliente e pelas estratégias de novas tentativas (*retries*).

* **Ajustes de Robustez e Correção de Casos:**
    * `faq_sem_resposta_ollama_real`: O modelo lidou corretamente com o cenário limite, injetando a tag `[PRECISA DE REVISÃO TÉCNICA]` no corpo e validando o comportamento esperado.
    * `faq_resposta_aceita_symfony_real`: Casos iniciais falharam por ausência da seção obrigatória `**Resposta curta:**`. O problema foi mitigado com o endurecimento do prompt em `adapter_faq.md` (reforçando a proibição de sinônimos como `**Resposta:**` ou `**Explicação:**`) e com validações dedicadas no `adapters_validator.py`.
    * `linkedin_conquista_sintetica`: Apresentou estouramentos esporádicos no limite de hashtags (gerando 7 quando o teto era 5). O comportamento foi normalizado com regras de correção integradas ao `adapters_prompt_builder.py` e validações de contagem no `adapters_validator.py`.

>[!TIP]
>Os resultados detalhados das execuções do Adapter estão documentados em [docs/benchmarks](../benchmarks/).

---

## 9. Changelog

### 0.4.0 (13/11/2026) — Refatoração Modular, Separação de Prompts e Arquitetura de Adapters

* **Documentação e Arquitetura:**
    * Criação da especificação arquitetural dedicadas ao pipeline de adapters (`adapters_architecture_spec.md`).
    * Documentação da decisão de arquitetura formalizada no ADR-005.
    * Separação dos resultados detalhados do benchmark em relatório consolidado em `docs/benchmarks/`.

* **Modularização dos Prompts de Adapters (`data/prompts/adapters/`):**
    * Fracionamento dos prompts monolíticos em arquivos Markdown independentes por canal (`adapter_blog.md`, `adapter_faq.md`, `adapter_linkedin.md`, `adapter_instagram.md`, `adapter_discord.md`, `adapter_mastodon.md`, `adapter_x_twitter.md`e `adapter_newsletter.md`).
    * Criação do `common_rules.md` para isolar diretrizes invioláveis e regras comuns aplicadas aos canais de redes sociais.
    * Implementação do `adapters_loader.py` para composição dinâmica e modular do System Prompt.

* **Mecanismo de Auto-Correção e Validação:**
    * Implementação do `adapters_prompt_builder.py` para formatação direcionada dos prompts de usuário e tratamento de reenvios em caso de erro.
    * Reforço das validações determinísticas no `adapters_validator.py` para estouramento de limites de caracteres, contagem de hashtags e obrigatoriedade de seções estruturadas.
    * Endurecimento dos prompts de FAQ para proibir sinônimos nas seções obrigatórias (`**Pergunta:**`, `**Resposta curta:**`, `**Fonte:**`).

* **Modularização do Pipeline:**
    * Refatoração do `eval_adapters.py` para atuar exclusivamente como orquestrador do benchmark.
    * Criação do `adapters_setup.py` para tratamento de argumentos da CLI, carregamento e validação inicial de casos.
    * Criação do `adapters_processor.py` para gerenciamento do ciclo de vida dos jobs, chamadas LLM e fluxo de retentativa/correção.
    * Criação do `adapters_report.py` para exibição via terminal, consolidação de métricas e persistência dos relatórios analíticos em JSON e CSV.

* **Métricas e Modos de Execução:**
    * Instrumentação de latência individual por job/requisição com `time.perf_counter()`.
    * Captura e consolidação de tokens de entrada, saída e totais fornecidos pelos provedores.

### 0.3.1 (24/10/2026), após revisão das saídas reais do Gemini
- Nada de "@" antes do nome: na 1ª rodada o X saiu com "@mike.dev", que marcaria outra conta no X. O validador agora barra menções com "@".
- Proibido acrescentar contexto que a pessoa não disse: o post do X falou em "transição", que não estava na entrada.
- "Solução relatada pela comunidade" só para resposta não aceita.
- FAQ: proibido citar classes ou bundles que não estão na resposta (a 1ª rodada citou um "AiBundle" que a resposta não nomeia).
- Newsletter: manter a incerteza do original e não acrescentar benefícios (a 1ª rodada transformou "perhaps" em certeza e incluiu "evitar consumo excessivo de recursos").

### 0.3.0 (24/10/2026)
- Alinhado ao `output_schema.json` do merge da PR #54: o X usa `target = "x/twitter"`; Bluesky saiu.
- Saídas geradas de verdade pelo Gemini com `src/pipeline/run_adapters.py`, a partir das classificações reais do Router v0.3.1.
- Temperatura 1.0 nos modelos Gemini 3, como recomenda o guia do Google.
- O FAQ devolve só os 4 campos do `output_schema.json` (`source_link` saiu; o link já vai na linha "Fonte").
- Saídas geradas de verdade pelo Gemini com `src/pipeline/run_adapters.py`, a partir das classificações reais do Router v0.3.1.
- Temperatura 1.0 nos modelos Gemini 3, como recomenda o guia do Google.

### 0.2.0 (21/10/2026)
- Saída com exatamente os 4 campos do `output_schema.json` (`char_count` saiu; o tamanho é recalculado no código).
- Linha de crédito obrigatória para conteúdo do Stack Overflow (CC BY-SA 4.0).
- Manter a incerteza do original e sinalizar resposta não aceita.
- Proibido inventar referência de tempo ("nesta semana").
- Lista de clichês proibidos ampliada; validação automática em `validate_adapters.py`.
- "Por que funciona" só aparece se a resposta original explicar o motivo. Na v0.1 essa seção convidava o modelo a inventar.
- Linha "Fonte" com autores e licença (CC BY-SA 4.0 exige atribuição).
- Resposta não aceita é sinalizada como "solução relatada pela comunidade".
- Newsletter não fala em "semana" quando o período não é de uma semana; Dica Rápida leva crédito; regra para "Em alta" quando os tópicos não se repetem.

### 0.1.0 (21/10/2026)
- Rascunho inicial.
