---
Projeto: CommunityLab - Motor Inteligente de Transformação e Distribuição para Comunidades Digitais
Versão: 1.0
Autor: Equipe 14 G10
Status: Aprovado
Elaboração: 13/11/2026
---

# ADR-005: Arquitetura do Sistema de Adaptação e Geração de Conteúdo

---

## Sumário

- [1. Contexto e Problema](#1-contexto-e-problema)
- [2. Decisão Tomada](#2-decisão-tomada)
  - [2.1. Princípios Arquiteturais](#21-princípios-arquiteturais)
  - [2.2. Organização dos Componentes](#22-organização-dos-componentes)
  - [2.3. Interação entre os Componentes](#23-interação-entre-os-componentes)
- [3. Alternativas Consideradas](#3-alternativas-consideradas)
  - [Manter toda a lógica em eval_adapters.py](#31-manter-toda-a-lógica-em-eval_adapterspy)
  - [3.2. Criar uma classe única para todo o Adapter](#32-criar-uma-classe-única-para-todo-o-adapter)
- [4. Consequências](#4-consequências)
  - [4.1. Benefícios](#41-benefícios)
  - [4.2. Limitações e Riscos](#42-limitações-e-riscos)
    
---

## 1. Contexto e Problema

O CommunityLab necessita transformar o conteúdo bruto normalizado (proveniente de threads técnicas e classificações do Router) em publicações estruturadas para múltiplos canais de engajamento (redes sociais, FAQs e newsletters semanais).

1. A lógica de orquestração de testes, construção de prompts, chamadas à API e validação estava concentrada em um único script monolítico (`eval_adapters.py`), dificultando a manutenção.
2. Cada canal (LinkedIn, X/Twitter, Mastodon, Instagram, Discord, FAQ, Newsletter) possui restrições editoriais estritas, limites de caracteres e regras específicas de formatação.
3. Obrigatoriedade de atribuição de licença (Stack Overflow CC BY-SA 4.0) diretamente no corpo do texto devido às limitações do output_schema.
4. Necessidade de checagens determinísticas rigorosas (tamanho de body, contagem de hashtags e emojis, bloqueio de menções com `@`) com suporte a ciclos de auto-correção (*retry*) em caso de falhas.
5. Suporte simultâneo a execuções unitárias por item (redes sociais e FAQ) e processamentos agregados em lote (Newsletter)

---

## 2. Decisão Tomada

Adotou-se uma **arquitetura modular baseada no Princípio da Responsabilidade Única (SRP)**, desacoplando o pipeline de adapters em módulos especializados localizados em `src/pipeline/` e organizando os prompts dinâmicos em `data/prompts/adapters/`.

O fluxo de execução obedece à seguinte pipeline estruturada:

```text
Casos de entrada (adapters_cases.json)
      |
      v
adapters_setup.py
      |
      v
eval_adapters.py (Orquestrador)
      |
      v
adapters_processor.py
      |
      +--> adapters_loader.py (Carrega common_rules.md + adapter_<canal>.md)
      |
      +--> adapters_prompt_builder.py (Monta prompt de usuário / fallback de retry)
      |
      +--> llm_providers.py --> llm_service.py --> APIs (Gemini/Groq/etc.)
      |
      +--> json_parser.py
      |
      +--> adapters_validator.py (Checagem determinística de limites, hashtags, etc.)
      |
      v
adapters_report.py
      |
      v
Relatório JSON, CSV e saída do benchmark (data/prompts/tests/outputs/)
```
A arquitetura separa explicitamente:
- A configuração da execução e CLI;
- A composição modular de prompts;
- A integração desacoplada com provedores LLM;
- O processamento individual ou em lote dos casos;
- A validação determinística de limites e regras de canal;
- A geração consolidada de relatórios.

### 2.1. Princípios Arquiteturais

- **Responsabilidade única**
Cada módulo deve possuir uma responsabilidade principal e bem delimitada dentro do ciclo de vida do pipeline.

- **Baixo acoplamento**
As regras de adaptação e geração de conteúdo não dependem da implementação específica de um provedor (como Gemini ou Groq).

* **Composição Modular de Prompts:** Separação entre as diretrizes transversais invioláveis (`common_rules.md`) e os templates específicos de cada canal (`adapter_<canal>.md`).

- **Validação determinística**
A resposta da LLM nunca é considerada válida apenas por retornar um JSON sintaticamente correto. O payload deve passar pelo `adapters_validator.py`, que valida limites de caracteres `(len(body))`, contagem de hashtags, emojis, ausência de menções com `@` e seções obrigatórias.

- **Observabilidade**
Cada execução registra, quando disponível:

  - Duração e latência da chamada;
  - Tokens de entrada, saída e totais;
  - Ocorrência de ciclo de retry corretivo;
  - Erros de parsing ou violação de regras de canal.

### 2.2. Organização dos Componentes

#### Prompts

Os prompts são mantidos em arquivos Markdown independentes (`data/prompts/adapters/`):

- `common_rules.md`: diretrizes transversais invioláveis (fidedignidade, isolamento de idioma em PT-BR, proibição de menções com @ e formatação estrita de código).;
- `adapter_<canal>.md`: regras editoriais específicas por canal (tamanho, tom de voz, estrutura de títulos e seções obrigatórias como em `adapter_faq.md`);

- `adapters_loader.py`: realiza a composição dinâmica do prompt base unindo as regras comuns ao template do canal de destino selecionado.

- `adapters_prompt_builder.py`: formata o prompt de usuário a partir do item normalizado e gerencia a injeção condicional de instruções corretivas ou exemplos de few-shot quando um ciclo de retry é acionado.

#### Configuração da execução

- `adapters_setup.py`:

      - Define os argumentos da CLI;
      - Seleciona os arquivos de casos de teste (`adapters_cases.json`);
      - Filtra casos pelo argumento `--only`;
      - Valida a disponibilidade da API Key;
      - Seleciona provedor, modelo e parâmetros de temperatura;
      - Inicializa o contexto de execução.

#### Orquestração

- `eval_adapters.py`:

      - Obtém os argumentos da CLI e inicializa o contexto;
      - Percorre os casos de teste configurados;
      - Despacha o processamento para o processador;
      - Chama o processador;
      - Encaminha os resultados consolidados para o relatório;
      - Define o código de saída da execução.

Não contém regras de parsing, chamadas de API ou lógica de validação.

#### Processamento

- `adapters_processor.py`:

      - Utiliza o `adapters_prompt_builder.py` para formatar os prompts de usuário;
      - Aciona a fachada `call_llm` via serviços de provedores (`llm_providers.py`);
      - Interpreta o JSON de resposta com o auxílio do `json_parser.py`;
      - Executa a validação determinística via `adapters_validator.py`;
      - Mede a latência com `time.perf_counter()` e coleta o uso de tokens;
      - Aciona uma segunda chamada corretiva quando houver falha de formato, estouro de limites ou violação de regras;
      - Reprocessa e revalida a segunda resposta;
      - Trata o modo `dry-run`.
      
#### Relatórios

- `adapters_report.py`:

      - Exibe o resultado detalhado de cada caso no terminal;
      - Exibe a taxa de acerto;
      - Calcula latência média e total;
      - Consolida os tokens das chamadas realizadas;
      - Registra resultados e metadados;
      - Salva o relatório JSON das execuções reais.

>[!NOTE]
>Tokens são considerados indisponíveis em `dry-run` sem métricas armazenadas.

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

- `adapters_validator.py`: 

      - Valida os payloads gerados contra os critérios da matriz global de limites (tamanho de body com len(body), contagem de hashtags e emojis por canal);
      - Verifica a conformidade do campo target com o enum suportado;
      - Bloqueia menções diretas com o caractere @ e detecta alucinações numéricas;
      - Verifica a presença de linhas de crédito obrigatórias (ex: licença CC BY-SA 4.0 do Stack Overflow).

### 2.3. Interação entre os Componentes

A execução do subsistema de Adapters segue uma cadeia clara de responsabilidades e fluxo de dados:

1. `adapters_setup.py` prepara o ambiente, valida credenciais e define os parâmetros de execução da CLI.
2. `eval_adapters.py` coordena a varredura e o loop de execução da suíte de casos de teste.
3. `adapters_processor.py` gerencia o ciclo de vida individual de cada job e aciona o carregamento dos prompts.
4. `adapters_loader.py` combina o arquivo de regras transversais (`common_rules.md`) com o template específico do canal de destino (`adapter_<canal>.md`).
5. `adapters_prompt_builder.py` formata o prompt de usuário com base no item normalizado.
6. Os serviços de LLM (`llm_providers.py` e `llm_service.py`) despacham a requisição para o provedor selecionado e normalizam a resposta bruta e as métricas de uso.
7. `adapters_validator.py` audita programaticamente a conformidade estrutural, o tamanho do corpo (`len(body)`), a contagem de hashtags/emojis e as restrições do canal.
8. `adapters_report.py` consolida as métricas operacionais (latência e tokens) e persiste os relatórios finais em JSON e CSV.

---

## 3. Alternativas Consideradas

### 3.1. Manter toda a lógica em `run_adapters.py`

Foi rejeitado porque concentrava CLI, carregamento de arquivos, requisições de API, parsing, validação estrita, controle de retries, métricas e persistência em um script monolítico, gerando alto acoplamento e impossibilitando testes unitários granulares.

### 3.2. Criar uma classe única para todo o Adapter

Foi rejeitado porque uma classe central continuaria acumulando responsabilidades distintas e poderia dificultar a substituição de componentes.

---

## 4. Consequências

### 4.1. Benefícios

- Redução do tamanho e da complexidade do `eval_adapters.py`, pois o script de entrada atua apenas como orquestrador;
- Responsabilidades claramente separadas;
- Menor acoplamento entre pipeline e provedores;
- Possibilidade de adicionar novos provedores;
- Validação independente e determinística;
- Prompts versionáveis e editáveis;
- Suporte a `dry-run`;
- Rastreabilidade de latência, uso de tokens e histórico de tentativas (retries)
- Maior facilidade para testes unitários.

### 4.2. Limitações e Riscos

- Violações de limite na primeira tentativa acionam uma chamada corretiva, dobrando o consumo de tokens naquele job específico.
- Modificações nos schemas de saída estritos exigem atualizações coordenadas nos prompts, validadores e suítes de teste.
- Diferenças de comportamento entre modelos podem influenciar a aderência estrita a formatações complexas de Markdown.