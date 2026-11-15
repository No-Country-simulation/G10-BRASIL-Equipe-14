---
Projeto: CommunityLab - Motor Inteligente de Transformação e Distribuição para Comunidades Digitais
Versão: 1.0
Autor: Equipe 14 G10
Status: Aprovado
Elaboração: 09/11/2026
---

# ADR-004: Arquitetura do Sistema de Roteamento e Classificação LLM

---

## Sumário

- [1. Contexto e Problema](#1-contexto-e-problema)
- [2. Decisão Tomada](#2-decisão-tomada)
  - [2.1. Princípios Arquiteturais](#21-princípios-arquiteturais)
  - [2.2. Organização dos Componentes](#22-organização-dos-componentes)
  - [2.3. Interação entre os Componentes](#23-interação-entre-os-componentes)
- [3. Alternativas Consideradas](#3-alternativas-consideradas)
  - [3.1. Manter toda a lógica em eval_router.py](#31-manter-toda-a-lógica-em-eval_routerpy)
  - [3.2. Criar uma classe única para todo o router](#32-criar-uma-classe-única-para-todo-o-router)
  - [3.3. Enviar os few-shot examples em todas as chamadas](#33-enviar-os-few-shot-examples-em-todas-as-chamadas)
  - [3.4. Confiar somente nos guardrails do Prompt](#34-confiar-somente-nos-guardrails-do-prompt)
- [4. Consequências](#4-consequências)
  - [4.1. Benefícios](#41-benefícios)
  - [4.2. Limitações e Riscos](#42-limitações-e-riscos)
    
---

## 1. Contexto e Problema

O CommunityLab precisa analisar threads provenientes de diferentes comunidades técnicas, incluindo Stack Overflow/Stack Exchange, Mastodon e Hacker News.

Cada thread deve ser classificada por um Router baseado em LLM, que identifica:

- tipo de conteúdo;
- sentimento;
- categoria temática;
- tópicos;
- idioma original;
- existência de resposta aceita;
- relevância;
- rota editorial ou operacional sugerida.

A implementação precisava atender simultaneamente aos seguintes requisitos:

1. Suportar mais de um provedor LLM;
2. Manter os prompts editáveis e versionáveis;
3. Separar regras de negócio da integração com APIs;
4. Validar deterministicamente as respostas do modelo;
5. Permitir execução normal, `dry-run` e `replay`;
6. Medir latência e uso de tokens;
7. Permitir correção de respostas inválidas sem carregar os exemplos *few-shot* em todas as chamadas;
8. Facilitar testes e evolução independente dos componentes.

A concentração dessas responsabilidades em um único arquivo dificultava a manutenção, aumentava o acoplamento e tornava mais difícil identificar a origem de falhas no pipeline.

---

## 2. Decisão Tomada

Adotou-se uma **arquitetura modular orientada ao Princípio da Responsabilidade Única (SRP)**, desacoplando o pipeline de router em módulos especializados localizados em `src/pipeline/` e organizando os prompts dinâmicos em `data/prompts/router/`.

O fluxo de execução obedece à seguinte pipeline estruturada:

```text
Casos de entrada  (router_cases_reais.json e router_cases_sinteticos.json)
      |
      v
router_setup.py
      |
      v
eval_router.py (Orquestrador)
      |
      v
router_processor.py
      |
      +--> router_loader.py (Carrega os prompts do router)
      |
      +--> router_prompt_builder.py (Monta prompt de usuário / fallback de retry)
      |
      +--> llm_providers.py --> llm_service.py --> APIs (Gemini/Groq/etc.)
      |
      +--> json_parser.py
      |
      +--> router_validator.py 
      |
      v
router_report.py
      |
      v
Relatório JSON, CSV e saída do benchmark (data/prompts/outputs/)
```

A arquitetura separa explicitamente:
- A configuração da execução e CLI;
- A composição modular de prompts;
- A integração desacoplada com provedores LLM;
- Processamento de casos;
- Validação determinística;
- A geração consolidada de relatórios.

### 2.1. Princípios Arquiteturais

- **Responsabilidade única**
Cada módulo deve possuir uma responsabilidade principal e bem delimitada dentro do ciclo de vida do pipeline.

- **Baixo acoplamento**
As regras de adaptação e geração de conteúdo não dependem da implementação específica de um provedor (como Gemini ou Groq).

- **Validação determinística**
O resultado do LLM não é considerado válido apenas por ser JSON. A saída deve passar pelo `router_validator.py`, que verifica **schema**, **enums**, **scores**, **has_answer**, **campos obrigatórios** e **rota esperada**.

- **Segurança em camadas**
Os prompts definem guardrails contra prompt injection, PII e exposição de segredos. O validador também deve rejeitar saídas incompatíveis com regras determinísticas de segurança.

- **Observabilidade**
Cada execução registra, quando disponível:

   - Duração e latência da chamada;
   - Tokens de entrada, saída e totais;
   - Ocorrência de retry;
   - Erros de parsing ou validação.

### 2.2. Organização dos Componentes

#### Prompts

Os prompts são mantidos em arquivos Markdown independentes:

- `system.md`: define o papel do Router e o contrato de saída;
- `evaluation_rubric.md`: define classificação, score e roteamento;
- `guardrails.md`: define regras de segurança e proteção de dados;
- `few_shot_examples.md`: contém exemplos usados para correção de formato e rótulos quando a primeira resposta falha.

- `router_loader.py`: carrega o prompt base sem os exemplos *few-shot*. Os exemplos são carregados separadamente e incluídos apenas em uma tentativa de correção.

- `router_prompt_builder.py`: formata o prompt de usuário a partir do item normalizado e gerencia a injeção condicional de instruções corretivas ou exemplos de few-shot quando um ciclo de retry é acionado.

#### Configuração da execução

- `router_setup.py`:

      - Define os argumentos da CLI;
      - Seleciona os arquivos de casos de teste (`router_cases.json`);
      - Filtra casos pelo argumento `--only`;
      - Carrega arquivos de replay;
      - Valida a disponibilidade da API Key;
      - Seleciona provedor, modelo e temperatura;
      - Carrega o prompt base e os exemplos *few-shot*;
      - Inicializa o contexto de execução.

#### Orquestração

- `eval_router.py`:

      - Obtém os argumentos da CLI e inicializa o contexto;
      - Percorre os casos de teste configurados;
      - Despacha o processamento para o processador;
      - Chama o processador;
      - Encaminha os resultados consolidados para o relatório;
      - Define o código de saída da execução.

Não contém regras de parsing, chamadas de API ou lógica de validação.

#### Processamento

- `router_processor.py`:

      - Utiliza o `router_prompt_builder.py` para formatar os prompts de usuário;
      - Aciona a fachada `call_llm` via serviços de provedores (`llm_providers.py`);
      - Interpreta o JSON de resposta com o auxílio do `json_parser.py`;
      - Executa a validação determinística via `router_validator.py`;
      - Mede a latência com `time.perf_counter()` e coleta o uso de tokens;
      - Aciona uma segunda chamada corretiva quando houver falha de formato, estouro de limites ou violação de regras;
      - Inclui os `few_shot_examples.md` somente na tentativa de correção;
      - Reprocessa e revalida a segunda resposta;
      - Trata os modos `dry-run` e `replay`.

A primeira chamada utiliza apenas:

```text
system.md
evaluation_rubric.md
guardrails.md
```

Quando necessário, a segunda chamada utiliza também:

```text
few_shot_examples.md
```

#### Relatórios

- `router_report.py`:

      - Exibe o resultado detalhado de cada caso no terminal;
      - Exibe a taxa de acerto;
      - Calcula latência média e total;
      - Consolida os tokens das chamadas realizadas;
      - Registra resultados e metadados;
      - Salva o relatório JSON das execuções reais.

>[!NOTE]
>Tokens são considerados indisponíveis em `dry-run` e `replay` sem métricas armazenadas.

#### Serviços de LLM

- `llm_providers.py`: mantém o registro de provedores e fornece a fachada `call_llm`.

- `llm_service.py`: implementa as chamadas específicas para os modelos selecionados e normaliza as respostas em uma estrutura comum, contendo texto e métricas de uso.

A escolha do provedor não deve alterar as regras de validação ou roteamento.

#### Utilitários

Os utilitários possuem responsabilidades compartilhadas:

- `cases_loader.py`: carrega casos e arquivos de histórico;
- `http_client.py`: executa requisições HTTP, timeout e retries de rede;
- `json_parser.py`: parsing seguro de respostas JSON brutas;
- `prompt_reader.py`: leitura de arquivos Markdown.
- `provider_config.py `: centraliza o mapeamento de configurações de cada provedor LLM;
- `regex_patterns.py`: centraliza as expressões regulares.

#### Validação

- `router_validator.py`:

      - Valida os casos de entrada contra o schema;
      - Valida campos obrigatórios;
      - Rejeita campos adicionais;
      - Valida enums e tipos;
      - Valida `topics`, `summary` e `relevance_score`;
      - Calcula a rota determinística;
      - Verifica `has_answer` com base em `raw_metadata.is_accepted`;
      - Verifica limites específicos para casos de segurança.

### 2.3. Interação entre os Componentes

A execução do subsistema de Router segue uma cadeia clara de responsabilidades e fluxo de dados:

1. `router_setup.py` prepara o ambiente, valida credenciais e define os parâmetros de execução da CLI.
2. `eval_router.py` coordena a varredura e o loop de execução da suíte de casos de teste.
3. `router_processor.py` gerencia o ciclo de vida individual de cada caso e aciona o carregamento dos prompts.
4. `router_loader.py` combina o arquivo de regras de prompts.
5. `router_prompt_builder.py` formata o prompt de usuário com base no item normalizado.
6. Os serviços de LLM (`llm_providers.py` e `llm_service.py`) despacham a requisição para o provedor selecionado e normalizam a resposta bruta e as métricas de uso.
7. `router_validator.py` valida a entrada e a saída do modelo.
8. `router_report.py` consolida as métricas operacionais (latência e tokens) e persiste os relatórios finais em JSON e CSV.

---

## 3. Alternativas Consideradas

### 3.1. Manter toda a lógica em `eval_router.py`

Foi rejeitado porque concentrava CLI, carregamento de arquivos, requisições de API, parsing, validação estrita, controle de retries, métricas e persistência em um script monolítico, gerando alto acoplamento e impossibilitando testes unitários granulares.

### 3.2. Criar uma classe única para todo o Router

Foi rejeitado porque uma classe central continuaria acumulando responsabilidades distintas e poderia dificultar a substituição de componentes.

### 3.3. Enviar os *few-shot examples* em todas as chamadas

Foi rejeitado porque aumenta o número de tokens de entrada em todos os casos, mesmo quando a primeira resposta já respeita o contrato.

### 3.4. Confiar somente nos guardrails do prompt

Foi rejeitado porque o LLM pode produzir JSON válido, mas semanticamente incompatível com as regras do sistema.

---

## 4. Consequências

### 4.1. Benefícios

- Redução do tamanho e da complexidade do `eval_router.py`, pois o script de entrada atua apenas como orquestrador;;
- Responsabilidades claramente separadas;
- Menor acoplamento entre pipeline e provedores;
- Possibilidade de adicionar novos provedores;
- Validação independente e determinística;
- Prompts versionáveis e editáveis;
- Redução do consumo de tokens nas chamadas bem-sucedidas;
- *few-shot examples* disponíveis para correção direcionada;
- Suporte a `dry-run` e `replay`;
- Rastreabilidade de latência, uso de tokens e histórico de tentativas (retries)
- Maior facilidade para testes unitários.

### 4.2. Limitações e Riscos

- A correção automática pode realizar uma segunda chamada e aumentar o consumo de tokens;
- Diferenças entre provedores podem afetar o formato ou a qualidade das respostas;
- `dry-run` não mede consumo real;
- `replay` só pode apresentar tokens se as métricas tiverem sido persistidas;
- Regras de segurança no prompt não substituem validação determinística;
- Alterações no contrato de saída exigem atualização dos prompts, validador, casos e testes;
- A composição condicional dos prompts precisa ser testada para evitar divergência entre primeira chamada e retry.
