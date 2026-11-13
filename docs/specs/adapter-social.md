---
Prompt_id: social_adapters
Issue: "#9 [S1-04] Desenvolver Prompts para as Redes Sociais"
Versão: 0.4.0
Autor: Equipe 14 G10 (Gustavo/Vitor)
Modelo: Gemini free tier (gemini-3.5-flash-lite ou gemini-3.1-flash-lite) | Groq
Temperatura: 1.0 nos modelos Gemini 3 (recomendação do Google); 0.0 nos demais
Entrada: saída do Router (rota success_case ou faq) + item original
Formato_saida: JSON compatível com um item de suggested_content (data/schemas/output_schema.json)
Elaborado em: 24/10/2026
Atualizado em: 13/11/2026
---

# Sistema de Adaptação e Geração de Conteúdo para Canais Sociais

O Sistema de Adaptação e Geração de Conteúdo para Canais Sociais é o componente responsável por consumir as saídas estruturadas do roteador, processar o contexto de threads técnicas e gerar publicações otimizadas para redes sociais de engajamento rápido (como LinkedIn, Mastodon, X/Twitter e Instagram). O subsistema garante o respeito estrito aos limites de caracteres, formatação de hashtags, emojis, remoção de menções indesejadas e aplicação padronizada de regras editoriais e de tom de voz.

---

## Sumário

- [1. Objetivo](#1-objetivo)
- [2. Visão Geral dos Canais Sociais](#2-visão-geral-dos-canais-sociais)
   - [2.1. Escopo de Canais Suportados](#21-escopo-de-canais-suportados)
- [3. Regras de Negócio e Restrições Editoriais](#3-regras-de-negócio-e-restrições-editoriais)
   - [3.1. Limites Estritos de Caracteres e Estruturas de Títulos](#31-limites-estritos-de-caracteres-e-estrutura-de-títulos)
   - [3.2. Regras Rígidas de Hashtags](#32-regras-rígidas-de-hashtags)
   - [3.3. Controle de Emojis e Menções](#33-controle-de-emojis-e-menções)
   - [3.4. Aplicação de Tom de Voz e Regras Comuns](#34-aplicação-de-tom-de-voz-e-regras-comuns)
   - [3.5. Matriz de Limites e Critérios de Aceite (Rede Social)](#35-matriz-de-limites-e-critérios-de-aceite-rede-social)
- [4. Estrutura dos System Prompts por Canal Social](#4-estrutura-dos-system-prompts-por-canal-social)
   - [4.1. Composição Modular](#41-composição-modular)
   - [4.2. Schema de Saída Consolidado](#42-schema-de-saída-consolidado)
- [5. Casos de Teste Específicos e Exemplos de Saída](#5-casos-de-teste-específicos-e-exemplos-de-saída)
   - [5.1. Exemplo de Saída: Post de Conquista](#51-exemplo-de-saída-post-de-conquista)
   - [5.2. Exemplo de Saída: Dica Técnica](#52-exemplo-de-saída-dica-técnica)
- [6.Changelog](#10-changelog)

---

## 1. Objetivo

A especificação do **Sistema de Adaptação para Canais Sociais (Social Adapters Spec)** tem como finalidade documentar as regras de negócio, as restrições editoriais estritas, os limites de caracteres e a formatação de System Prompts específicos para redes sociais de engajamento rápido (como **LinkedIn**, **X/Twitter**, **Mastodon**, **Instagram** e **Discord/Blog**). O subsistema visa garantir a conformidade com o tom de voz corporativo, o controle rigoroso de contagem de hashtags e emojis, a proibição de menções indesejadas com `@` e a aplicação padronizada das regras comuns compartilhadas.

---

## 2. Visão Geral dos Canais Sociais

O subsistema social opera de forma desacoplada, recebendo os dados normalizados de threads técnicas e adaptando o conteúdo bruto em formatos otimizados para rápida absorção e engajamento nas plataformas de destino.

### 2.1. Escopo de Canais Suportados

* **LinkedIn (`adapter_linkedin.md`):** Focado em conquistas profissionais, dicas técnicas estruturadas e reflexões de engenharia. Exige formatação limpa e uso moderado de hashtags corporativas.
* **X/Twitter (`adapter_x_twitter.md`) e Mastodon (`adapter_mastodon.md`):** Voltados para microblogs, exigindo concisão, síntese de conceitos complexos e cumprimento estrito de limites restritos de caracteres.
* **Instagram (`adapter_instagram.md`):** Focado em chamadas visuais, ganchos dinâmicos e blocos estruturados para carrosséis ou legendas de alto impacto.
* **Outros Canais (`adapter_blog.md`, `adapter_discord.md`):** Canais de suporte para distribuição complementar de conteúdos adaptados.

---

## 3. Regras de Negócio e Restrições Editoriais

O processamento dos adaptadores sociais é regido por restrições rígidas para garantir que o conteúdo gerado atenda exatamente aos padrões de formatação e às limitações técnicas de cada plataforma, evitando truncamentos e desalinhamentos de tom.

### 3.1. Limites Estritos de Caracteres e Estrutura de Títulos

Cada canal possui um teto máximo e uma estrutura recomendada de extensão para o corpo do texto e para o título (quando aplicável):

* **LinkedIn:** Limite ideal de caracteres focado em leitura fluida (estruturado com ganchos de abertura, desenvolvimento em tópicos e chamada para ação).
* **X/Twitter e Mastodon:** Rigor técnico para respeitar os limites estritos de caracteres por post, exigindo concisão e síntese direta de soluções técnicas.
* **Instagram:** Foco em ganchos visuais e formatação em blocos espaçados para legibilidade em dispositivos móveis.

### 3.2. Regras Rígidas de Hashtags

* **Contagem Obrigatória:** As redes sociais exigem um intervalo estrito de hashtags (tipicamente entre 3 e 5 hashtags relevantes por publicação).
* **Validação de Excesso:** Caso o modelo gere um número de hashtags superior ao teto (como observado em testes de estresse em posts sintéticos do LinkedIn), o mecanismo de validação (`adapters_validator.py`) intercepta a falha e aciona o ciclo de auto-correção via `adapters_prompt_builder.py`.

### 3.3. Controle de Emojis e Menções

* **Uso de Emojis:** Devem ser aplicados de forma moderada e contextual, servindo como marcadores visuais de seções sem poluir a leitura técnica.
* **Bloqueio de Menções:** É estritamente proibida a inclusão de menções diretas com o caractere `@` no corpo das publicações geradas para os canais sociais, mitigando riscos de marcação indevida de perfis.

### 3.4. Aplicação de Tom de Voz e Regras Comuns

O arquivo `common_rules.md` atua como uma barreira transversal de formatação injetada no System Prompt de todos os canais sociais, estabelecendo:

* O tom técnico, profissional e direto;
* A proibição de ganchos clichês excessivos ou linguagem de marketing agressiva;
* A padronização na remoção de blocos de código excessivamente longos que não se adequem ao formato de uma rede social (convertendo-os para trechos inline ou resumos conceituais).

### 3.5. Matriz de Limites e Critérios de Aceite (Rede Social)
 
Cada canal monitorado pelo subsistema submete-se rigidamente aos seguintes parâmetros checados de forma automatizada:
| Canal | Limite de `body` | Hashtags | Emojis |
|:-----:|:----------------:|:--------:|:------:|
| linkedin | 600–1.300 | 3–5 | ≤ 3 |
| x/twitter | ≤ 280 | 1–2 | livre |
| mastodon | ≤ 500 | ≤ 2 | livre |
| instagram | ≤ 2.200 | 5–10 | ≤ 5 |
| discord | ≤ 2.000 | 0–2 | livre |
| blog | 500–5.000 | 0–5 | livre |

Na matriz acima estão destacadas somente os limites por canal social.

---

## 4. Estrutura dos System Prompts por Canal Social

O carregamento e a composição dos prompts dos canais sociais são gerenciados de forma dinâmica pelo `adapters_loader.py`, garantindo que as diretrizes gerais e as regras específicas de cada plataforma sejam aplicadas de maneira isolada.

### 4.1. Composição Modular

Para qualquer canal social de destino (como LinkedIn, X/Twitter, Mastodon, Instagram, Blog ou Discord), o prompt de sistema enviado à LLM é composto pela união de duas camadas principais:

1. **Regras Invioláveis Transversais (`common_rules.md`):** Estabelecem as diretrizes fundamentais de fidedignidade aos dados de entrada, isolamento de idioma (Português do Brasil), proibição de menções diretas com o caractere `@` (exigindo formato limpo como `mike.dev`), tratamento estrito de blocos de código sem refatorações automáticas, e a obrigatoriedade de atribuição de licença (Stack Overflow CC BY-SA 4.0) quando aplicável.

2. **Diretrizes Específicas do Canal (`adapter_<canal>.md`):** Definem o tom de voz editorial (ex: inspirador para o LinkedIn, direto e levemente humorado para o X/Twitter, ou visual e motivador para o Instagram), os limites estritos de caracteres, o teto de emojis e a contagem obrigatória de hashtags.

### 4.2. Schema de Saída Consolidado

Independentemente do canal social selecionado, todas as respostas geradas pelo modelo devem retornar estritamente um objeto JSON cru e válido (sem cercas de código markdown ou saudações) contendo os seguintes campos obrigatórios:

```json
{
  "target": "<canal_social>",
  "title": "<título interno ou descrição para curadoria>",
  "body": "<texto final pronto para publicar, já formatado e com hashtags>",
  "potential_engagement": "low" | "medium" | "high"
}

```

---

## 5. Casos de Teste Específicos e Exemplos de Saída

O comportamento dos adaptadores sociais é validado com base em casos reais e sintéticos que cobrem diferentes abordagens editoriais (conquistas e dicas técnicas):

### 5.1. Exemplo de Saída: Post de Conquista

* **Caso de origem:** `linkedin_conquista_sintetica`
* **Comportamento esperado:** Gancho focado em curiosidade (sem clichês corporativos), citação estruturada, parágrafos curtos, contagem de 3 a 5 hashtags e até 3 emojis.


* **Estrutura do JSON gerado:**

```json
{
  "target": "linkedin",
  "title": "Aprovação como Engenheira de Dados Jr na Stone",
  "body": "Depois de 1 ano de estudos intensos e muita dedicação, a carla_data foi aprovada como Engenheira de Dados Jr na Stone 🚀\n\nDurante todo o processo seletivo, o projeto prático de pipeline desenvolvido com n8n e OCI na comunidade foi o grande destaque, sendo o principal assunto discutido em todas as etapas da entrevista técnica.\n\nHistórias inspiradoras como a da carla mostram claramente como o foco nos estudos aliado à prática em projetos reais fazem toda a diferença na consolidação de uma carreira de sucesso na área de tecnologia.\n\nQueremos saber: o que você tem construído e colocado no seu portfólio esta semana? Conta pra gente aqui nos comentários e vamos trocar ideias sobre a sua jornada!\n\n#EngenhariaDeDados #Carreira #OracleNextEducation #Tecnologia #Dados",
  "potential_engagement": "high"
}

```

### 5.2. Exemplo de Saída: Dica Técnica

* **Caso de origem:** `x_dica_tecnica_real` (baseado em thread técnica)
* **Comportamento esperado:** Concisão extrema, limite de até 280 caracteres, inclusão direta do comando essencial e uso de 1 a 2 hashtags.

* **Estrutura do JSON gerado:**

```json
{
  "target": "x/twitter",
  "title": "Desativar botao de commit por IA no VS Code",
  "body": "Quer remover só o botão de gerar commit por IA no VS Code sem desligar o Copilot Chat? Adicione \"scm.showInputActionButton\": false nas configurações (JSON). Fonte: Stack Overflow, pergunta de Stevoisiak e resposta de Michael (CC BY-SA 4.0). #VSCode #Dev",
  "potential_engagement": "medium"
},

```

---

## 6. Changelog

### 0.4.0 (13/11/2026) — Refatoração e Padronização dos Canais Sociais
- Isolamento das regras comuns e diretrizes invioláveis no arquivo `common_rules.md`.
- Criação dos prompts específicos para LinkedIn, X/Twitter, Mastodon, Instagram, Discord e Blog.
- Ajuste nas restrições de contagem de hashtags e limites de caracteres para atender rigorosamente à matriz de critérios de aceite automatizados.
- Integração do fluxo de correção automática em caso de estouro de tamanho ou uso incorreto de caracteres especiais.

### 0.3.1 (24/10/2026), após revisão das saídas reais do Gemini
- Nada de "@" antes do nome: na 1ª rodada o X saiu com "@mike.dev", que marcaria outra conta no X. O validador agora barra menções com "@".
- Proibido acrescentar contexto que a pessoa não disse: o post do X falou em "transição", que não estava na entrada.
- "Solução relatada pela comunidade" só para resposta não aceita.

### 0.3.0 (24/10/2026)
- Alinhado ao `output_schema.json` do merge da PR #54: o X usa `target = "x/twitter"`; Bluesky saiu.
- Saídas geradas de verdade pelo Gemini com `src/pipeline/run_adapters.py`, a partir das classificações reais do Router v0.3.1.
- Temperatura 1.0 nos modelos Gemini 3, como recomenda o guia do Google.

### 0.2.0 (21/10/2026)
- Saída com exatamente os 4 campos do `output_schema.json` (`char_count` saiu; o tamanho é recalculado no código).
- Linha de crédito obrigatória para conteúdo do Stack Overflow (CC BY-SA 4.0).
- Manter a incerteza do original e sinalizar resposta não aceita.
- Proibido inventar referência de tempo ("nesta semana").
- Lista de clichês proibidos ampliada; validação automática em `validate_adapters.py`.

### 0.1.0 (21/10/2026)
- Rascunho inicial.
