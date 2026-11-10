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
- [4. Consequências](#3-consequências)
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

Adotou-se uma arquitetura modular orientada ao Princípio da Responsabilidade Única (*Single Responsibility Principle*).

Cada camada possui uma responsabilidade específica:

```text
Casos de entrada
      |
      v
router_setup.py
      |
      v
eval_router.py
      |
      v
router_processor.py
      |
      +--> llm_providers.py --> llm_service.py --> APIs Gemini/Groq/etc.
      |
      +--> json_parser.py
      |
      +--> router_validator.py
      |
      v
router_report.py
      |
      v
Relatório JSON e saída do benchmark
```

A arquitetura também separa:

- Configuração da execução;
- Composição de prompts;
- Integração com provedores;
- Processamento de casos;
- Validação determinística;
- Geração de relatórios.

### 2.1. Princípios Arquiteturais

- **Responsabilidade única**
Cada módulo deve possuir uma responsabilidade principal e bem delimitada.

- **Baixo acoplamento**
As regras de classificação não devem depender da implementação específica de Gemini ou Groq.

- **Validação determinística**
O resultado do LLM não é considerado válido apenas por ser JSON. A saída deve passar pelo `router_validator.py`, que verifica **schema**, **enums**, **scores**, **has_answer**, **campos obrigatórios** e **rota esperada**.

- **Segurança em camadas**
Os prompts definem guardrails contra prompt injection, PII e exposição de segredos. O validador também deve rejeitar saídas incompatíveis com regras determinísticas de segurança.

- **Observabilidade**
Cada execução deve registrar, quando disponível:

   - Duração da chamada;
   - Tokens de entrada;
   - Tokens de saída;
   - Tokens totais;
   - Ocorrência de retry;
   - Erros de parsing ou validação.

### 2.2. Organização dos Componentes
#### Prompts

Os prompts são mantidos em arquivos Markdown independentes:

- `system.md`: define o papel do Router e o contrato de saída;
- `evaluation_rubric.md`: define classificação, score e roteamento;
- `guardrails.md`: define regras de segurança e proteção de dados;
- `few_shot_examples.md`: contém exemplos usados para correção de formato e rótulos quando a primeira resposta falha.

O [router_loader.py](../../src/pipeline/router_loader.py) carrega o prompt base sem os exemplos *few-shot*. Os exemplos são carregados separadamente e incluídos apenas em uma tentativa de correção.

#### Configuração da execução

O [router_setup.py](../../src/pipeline/router_setup.py):

- Define os argumentos da CLI;
- Seleciona os arquivos de casos;
- Filtra casos pelo argumento `--only`;
- Carrega arquivos de replay;
- Valida a disponibilidade da API Key;
- Seleciona provedor, modelo e temperatura;
- Carrega o prompt base e os exemplos *few-shot*;
- Cria o contexto de execução.

#### Orquestração

O [eval_router.py](../../src/pipeline/eval_router.py) é o ponto de entrada do benchmark. Ele:

- Obtém os argumentos da CLI;
- Solicita o contexto de execução;
- Percorre os casos;
- Chama o processador;
- Encaminha os resultados para o relatório;
- Define o código de saída da execução.

Ele não deve conter regras de parsing, classificação, integração com APIs ou persistência detalhada.

#### Processamento

O [router_processor.py](../../src/pipeline/router_processor.py):

- Monta o prompt de usuário;
- Chama a fachada `call_llm`;
- Interpreta a resposta JSON;
- Executa a validação;
- Mede a duração;
- Coleta o uso de tokens;
- Executa uma segunda chamada quando houver erro de formato ou rótulo;
- Inclui os *few-shot examples* somente na tentativa de correção;
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

O [router_report.py](../../src/pipeline/router_report.py):

- Exibe o resultado de cada caso;
- Exibe a taxa de acerto;
- Calcula latência média e total;
- Consolida os tokens das chamadas realizadas;
- Registra resultados e metadados;
- Salva o relatório JSON das execuções reais.

Tokens são considerados indisponíveis em `dry-run` e em `replay` sem métricas armazenadas.

#### Serviços de LLM

O [llm_providers.py](../../src/services/llm_providers.py) mantém o registro de provedores e fornece a fachada `call_llm`.

O [llm_service.py](../../src/services/llm_service.py) implementa as chamadas específicas para os modelos selecionados e normaliza as respostas em uma estrutura comum, contendo texto e métricas de uso.

A escolha do provedor não deve alterar as regras de validação ou roteamento.

#### Utilitários

Os utilitários possuem responsabilidades compartilhadas:

- `prompt_reader.py`: lê arquivos Markdown;
- `cases_loader.py`: carrega casos e arquivos de replay;
- `json_parser.py`: interpreta respostas JSON;
- `http_client.py`: executa requisições HTTP, timeout e retries de rede.

#### Validação

O [router_validator.py](../../src/validation/router_validator.py):

- Valida os casos de entrada contra o schema;
- Valida campos obrigatórios;
- Rejeita campos adicionais;
- Valida enums e tipos;
- Valida `topics`, `summary` e `relevance_score`;
- Calcula a rota determinística;
- Verifica `has_answer` com base em `raw_metadata.is_accepted`;
- Verifica limites específicos para casos de segurança.

#### Testes Unitários
O [test_router_validator.py](`tests/test_router_validator.py`):**

- Contém os testes unirários das regras de validação, incluindo tipos, campos obrigatórios, enums, faixas de score, rotas e rejeição de campos adicionais.

### 2.3. Interação entre os Componentes

A execução do Router segue uma cadeia de responsabilidades:

1. `router_setup.py` prepara o contexto da execução.
2. `eval_router.py` coordena o processamento dos casos.
3. `router_processor.py` processa cada caso e interage com os serviços de LLM.
4. `router_validator.py` valida a entrada e a saída do modelo.
5. `router_report.py` consolida e persiste os resultados.

---

## 3. Alternativas Consideradas

### 3.1. Manter toda a lógica em `eval_router.py`

Foi rejeitado porque concentrava:

- CLI;
- carregamento;
- chamadas LLM;
- parsing;
- validação;
- retries;
- métricas;
- persistência.

Essa abordagem aumentava o acoplamento e dificultava os testes.

### 3.2. Criar uma classe única para todo o Router

Foi rejeitado porque uma classe central continuaria acumulando responsabilidades distintas e poderia dificultar a substituição de componentes.

### 3.3. Enviar os *few-shot examples* em todas as chamadas

Foi rejeitado porque aumenta o número de tokens de entrada em todos os casos, mesmo quando a primeira resposta já respeita o contrato.

### 3.4. Confiar somente nos guardrails do prompt

Foi rejeitado porque o LLM pode produzir JSON válido, mas semanticamente
incompatível com as regras do sistema.

---

## 4. Consequências

### 4.1. Benefícios

- Redução do tamanho e da complexidade do `eval_router.py`;
- Responsabilidades claramente separadas;
- Menor acoplamento entre pipeline e provedores;
- Possibilidade de adicionar novos provedores;
- Validação independente e determinística;
- Prompts versionáveis e editáveis;
- Redução do consumo de tokens nas chamadas bem-sucedidas;
- *few-shot examples* disponíveis para correção direcionada;
- Suporte a `dry-run` e `replay`;
- Medição consolidada de latência e tokens;
- Maior facilidade para testes unitários.

### 4.2. Limitações e Riscos

- A correção automática pode realizar uma segunda chamada e aumentar o consumo de tokens;
- Diferenças entre provedores podem afetar o formato ou a qualidade das respostas;
- `dry-run` não mede consumo real;
- `replay` só pode apresentar tokens se as métricas tiverem sido persistidas;
- Regras de segurança no prompt não substituem validação determinística;
- Alterações no contrato de saída exigem atualização dos prompts, validador, casos e testes;
- A composição condicional dos prompts precisa ser testada para evitar divergência entre primeira chamada e retry.
