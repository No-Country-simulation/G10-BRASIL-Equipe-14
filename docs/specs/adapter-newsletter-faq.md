---
Prompt_id: newsletter_faq
Issue: "#10 [S1-05] Desenvolver Prompts para Newsletter e FAQ Dinâmico"
Versão: 0.4.0
Autor: Equipe 14 G10 (Gustavo/Vitor)
Modelo: Gemini free tier (gemini-3.5-flash-lite ou gemini-3.1-flash-lite) | Groq
Temperatura: 1.0 nos modelos Gemini 3 (recomendação do Google); 0.0 nos demais
Entrada: saída do Router (rota success_case ou faq) + item original
Formato_saida: JSON compatível com um item de suggested_content (data/schemas/output_schema.json)
Elaborado em: 24/10/2026
Atualizado em: 13/11/2026

---

# Sistema de Adaptação para FAQ e Newsletter

O Sistema de Adaptação para FAQ e Newsletter é o componente responsável por agregar múltiplos itens classificados pelo roteador (no caso de newsletters semanais) ou transformar dúvidas técnicas complexas em cards padronizados de FAQ (com seções obrigatórias estruturadas como **Pergunta:**, **Resposta curta:** e **Fonte:**). O subsistema gerencia fluxos de revisão técnica obrigatória (`[PRECISA DE REVISÃO TÉCNICA]`), verificação de licenças de código aberto e formatação editorial aprofundada.

---

## Sumário

- [1. Objetivo](#1-objetivo)
- [2. Visão Geral dos Canais de FAQ e Newsletter](#2-visão-geral-dos-canais-de-faq-e-newsletter)
   - [2.1. Escopo de Canais Suportados](#21-escopo-de-canais-suportados)
- [3. Regras de Negócio e Restrições Editoriais](#3-regras-de-negócio-e-restrições-editoriais)
   - [3.1. Seções de Cards de FAQ](#31-seções-de-cards-de-faq)
   - [3.2. Estrutura Editorial de Newsletter](#32-estrutura-editorial-de-newsletter)
   - [3.3. Matriz de Limites e Critérios de Aceite (FAQ e Newsletter)](#33-matriz-de-limites-e-critérios-de-aceite-faq-e-newsletter)
   - [3.4. Regra de Execução (FAQ vs Newsletter)](#34-regra-de-execução-faq-vs-newsletter)
- [4. Estrutura dos System Prompts (FAQ e Newsletter)](#4-estrutura-dos-system-prompts-faq-e-newsletter)
   - [4.1. Schema de Saída Consolidado](#41-schema-de-saída-consolidado)
- [5. Casos de Teste Específicos e Exemplos de Saída](#5-casos-de-teste-específicos-e-exemplos-de-saída)
   - [5.1. Exemplo de Saída: Card de FAQ](#51-exemplo-de-saída-card-de-faq)
   - [5.2. Exemplo de Saída: Edição de Newsletter](#52-exemplo-de-saída-edição-de-newsletter)
- [6.Changelog](#6-changelog)

---

## 1. Objetivo

A especificação do **Sistema de Adaptação para FAQ e Newsletter** tem como finalidade documentar as regras de estruturação de cards de perguntas frequentes, a curadoria e síntese de lotes para newsletters editoriais, as restrições estritas de formatação e os critérios de validação de robustez. O subsistema visa transformar dúvidas técnicas complexas da comunidade em FAQs padronizadas de alta utilidade e consolidar edições semanais engajadas, mantendo o rigor técnico e o alinhamento com as diretrizes editoriais do programa.

---

## 2. Visão Geral dos Canais de FAQ e Newsletter

O subsistema de curadoria e FAQ atua processando tanto itens isolados quanto lotes consolidados de interações técnicas, convertendo dados brutos (frequentemente em inglês e formatos complexos) em conteúdos estruturados de fácil absorção.

### 2.1. Escopo de Canais Suportados

* **FAQ (`adapter_faq.md`):** Focado na transformação de dúvidas reais da comunidade em cards estruturados compostos por seções rígidas obrigatórias (`**Pergunta:**`, `**Resposta curta:**` e `**Fonte:**`), além do tratamento especial para itens sem solução (inclusão da tag de revisão técnica).

* **Newsletter (`adapter_newsletter.md`):** Voltado para a edição de boletins periódicos semanais, estruturados com abertura editorial, vitórias da comunidade, dicas rápidas, destaques de tópicos em alta e fechamento contextual.

---

## 3. Regras de Negócio e Restrições Editoriais

O processamento dos adaptadores de FAQ e Newsletter exige um rigor estrutural elevado para garantir a padronização dos cards de conhecimento e a coesão editorial das edições semanais.

### 3.1. Seções de Cards de FAQ

Os cards gerados a partir de dúvidas da comunidade devem seguir estritamente o formato descritivo padronizado:

* **Seções Obrigatórias:** O corpo do card deve conter obrigatoriamente e com exatidão os nomes das seções: `**Pergunta:**`, `**Resposta curta:**` e `**Fonte:**`. É terminantemente proibido o uso de sinônimos como `**Resposta:**`, `**Explicação:**` ou `**Solução:**`.

* **Seções Condicionais:**
   * `**Exemplo:**` (bloco de código mínimo copiado exatamente da resposta original; incluído somente se houver código).

   * `**Por que funciona:**` (1 a 2 frases explicativas; incluído somente se a fonte contiver a justificativa técnica).

* **Tratamento de Itens Sem Solução:** Caso o item de origem não possua uma resposta validada ou aceita, o modelo deve ignorar a geração de solução comum, definir o engajamento como `"low"` e iniciar o `body` obrigatoriamente com a tag de controle `[PRECISA DE REVISÃO TÉCNICA]` seguida apenas da pergunta reescrita, omitindo as demais seções do card.

### 3.2. Estrutura Editorial de Newsletter

As edições semanais consolidadas são geradas a partir de um lote de itens previamente classificados pelo **Router**, obedecendo rigorosamente à seguinte ordem estrutural:

1. **Abertura:** 2 frases definindo o clima da semana, citando os 2 ou 3 temas mais frequentes em "topics", proibindo saudações genéricas.

2. **🏆 Vitórias da Semana:** Até 3 itens com conquistas ou depoimentos positivos ordenados por relevância (relevance_score).

3. **💡 Dica Rápida:** A dúvida técnica de maior relevância com resposta aceita, transformada em um mini-tutorial de até 5 linhas.

4. **🔥 Em alta na comunidade:** Até 5 tópicos mais frequentes em formato de lista (*bullet points*), com 1 linha cada..

5. **Fechamento:** 1 frase contendo um convite para participar (responder, postar a própria dúvida ou conquista).

* **Filtro de Descarte:** Itens marcados com `suggested_route` igual a `"moderation"` ou `"discard"` são estritamente filtrados e banidos da newsletter.

### 3.3. Matriz de Limites e Critérios de Aceite (FAQ e Newsletter)

Os parâmetros quantitativos checados de forma automatizada pelo validador para este subsistema compreendem:

| Canal | Limite de `body` | Hashtags | Emojis |
| --- | --- | --- | --- |
| `faq` | ≤ 1.200 | 0 | livre |
| `newsletter` | ≤ 3.000 | 0 | livre |

### 3.4. Regra de Execução (FAQ vs Newsletter):

- **FAQ:** Roda por item, para cada interação com rota faq no Router.
- **Newsletter:** Roda uma vez por lote/semana, recebendo a lista de itens já classificados do reference_period.

>[!WARNING]
>Atenção à Licença (Stack Overflow): O conteúdo do Stack Overflow é licenciado sob CC BY-SA, exigindo atribuição obrigatória. Por isso, o card de FAQ e as dicas da newsletter sempre levam a linha "Fonte" com autores, licença e hiperlink dentro do próprio body, uma vez que o schema de saída estrito (output_schema.json) não aceita campos extras.

---

## 4. Estrutura dos System Prompts (FAQ e Newsletter)

O carregamento e a composição dos prompts dos canais de faq e newsletter são gerenciados de forma dinâmica pelo `adapters_loader.py`, garantindo que as diretrizes gerais e as regras específicas definidas nos prompts sejam aplicadas de maneira isolada. 

### 4.1. Schema de Saída Consolidado

Independentemente do canal de destino (FAQ ou Newsletter), todas as respostas geradas pelo modelo seguem um contrato estrito, retornado exclusivamente como um objeto JSON cru e válido, sem cercas de código markdown (code fences) ou saudações, contendo a seguinte estrutura padronizada:

```json
{
  "target": "<faq | newsletter>",
  "title": "<título ou pergunta formatada conforme restrições do canal>",
  "body": "<conteúdo completo formatado em Markdown simples>",
  "potential_engagement": "low" | "medium" | "high"
}

```

---

## 5. Casos de Teste Específicos e Exemplos de Saída

O comportamento dos adaptadores de FAQ e Newsletter é validado com base em casos reais e sintéticos que cobrem tanto a estruturação de cards de conhecimento quanto a consolidação de boletins semanais.

### 5.1. Exemplo de Saída: Card de FAQ

* **Caso de origem:** `faq_resposta_aceita_vscode_real` (baseado em dúvida técnica resolvida)
* **Comportamento esperado:** Pergunta iniciada obrigatoriamente por "Como", "Por que" ou "O que" (máximo 80 caracteres), corpo estruturado estritamente com as seções obrigatórias **Pergunta:**, **Resposta curta:** e **Fonte:**, sem utilização de sinônimos, e teto máximo de 1.200 caracteres.

* **Estrutura do JSON gerado:**

```json
{
  "target": "faq",
  "title": "Como desativar o botão de commit por IA no VS Code?",
  "body": "**Pergunta:** Como remover o botão de gerar mensagem de commit por IA no VS Code sem desativar os demais recursos de inteligência artificial?\n\n**Resposta curta:** Você pode ocultar especificamente esse botão ajustando as configurações do editor no arquivo JSON de preferências do usuário. Adicione a propriedade responsável por controlar a exibição dos botões de ação na caixa de entrada do SCM.\n\n**Exemplo:**\n```json\n\"scm.showInputActionButton\": false\n```\n\n**Por que funciona:** Essa configuração específica oculta o botão de ação na interface do painel de controle de código-fonte (SCM), desativando apenas esse atalho sem afetar o GitHub Copilot ou o chat.\n\n**Próximos passos:** Explore outras configurações do painel SCM no VS Code para personalizar ainda mais o seu fluxo de trabalho.\n\n**Fonte:** Stack Overflow, pergunta de Stevoisiak e resposta de Michael (CC BY-SA 4.0). https://stackoverflow.com/questions/79998781/how-do-i-disable-generate-commit-message-without-disabling-other-ai-features-i",
  "potential_engagement": "medium"
}
```

### 5.2. Exemplo de Saída: Edição de Newsletter

* **Caso de origem:** `newsletter_lote_real` (lote com múltiplos itens classificados)
* **Comportamento esperado:** Abertura editorial direta sem saudações genéricas, seção de vitórias, dica rápida com maior relevância, tópicos em alta em lista (bullet points) e fechamento contextual, mantendo o limite estrito de 3.000 caracteres.

* **Estrutura do JSON gerado:**

```json
{
  "target": "newsletter",
   "title": "CommunityLab: Python, LlamaIndex e IA no código",
   "body": "Esta semana, nossa comunidade focou forte em integrações com Python, LlamaIndex e o uso prático de ferramentas de IA no desenvolvimento. O ritmo está acelerado e cheio de novidades técnicas.\n\n### 💡 Dica Rápida\nAo rodar modelos locais no LlamaIndex com o Ollama, você pode esbarrar em um erro de 500 informando que o modelo exige mais memória do que o disponível. Isso acontece porque o LlamaIndex tenta carregar o modelo base durante a chamada de metadados, mesmo que você especifique uma versão menor como o `phi3:mini`. A solução simples é definir explicitamente uma janela de contexto na inicialização do objeto:\n\n```python\nfrom llama_index.llms.ollama import Ollama\n\nllm = Ollama(\n    model=\"phi3:mini\",\n    temperature=0.7,\n    max_tokens=100,\n    context_window=8000,\n)\n```\n\nFonte: pergunta de Kemp e resposta de Ajeet Verma no Stack Overflow (CC BY-SA 4.0).\n\n### 🔥 Em alta na comunidade\n- Python e LlamaIndex\n- Integração com Ollama\n- Symfony AI e LM Studio\n- Produtividade com VS Code\n- O futuro da carreira dev com IA\n\nResponda este e-mail compartilhando sua principal conquista ou dúvida técnica da semana!",
   "potential_engagement": "high"
}

```

---

## 6. Changelog

### 0.4.0 (13/11/2026) — Refatoração e Padronização dos Canais de FAQ e Newsletter
- Criação dos prompts modulares específicos para o canal de FAQ (`adapter_faq.md`) e de Newsletter (`adapter_newsletter.md`).
- Implementação de regras estritas para cards de FAQ, exigindo as seções obrigatórias (`**Pergunta:**`, `**Resposta curta:**` e `**Fonte:**`) e proibindo terminantemente o uso de sinônimos estruturais.
- Inclusão do mecanismo de fallback para itens sem solução, injetando obrigatoriamente a tag de controle `[PRECISA DE REVISÃO TÉCNICA]`.
- Padronização do fluxo editorial de newsletters semanais, garantindo a ordem estruturada (Abertura, Vitórias, Dica Rápida, Tópicos em Alta e Fechamento) e a aplicação do filtro de descarte para rotas de moderação.
- Alinhamento dos limites estritos de caracteres e critérios de validação automatizada para conformidade com a matriz global de aceites.

### 0.3.1 (24/10/2026), após revisão das saídas reais do Gemini
- FAQ: proibido citar classes ou bundles que não estão na resposta (a 1ª rodada citou um "AiBundle" que a resposta não nomeia).
- Newsletter: manter a incerteza do original e não acrescentar benefícios (a 1ª rodada transformou "perhaps" em certeza e incluiu "evitar consumo excessivo de recursos").

### 0.3.0 (24/10/2026)
- O FAQ devolve só os 4 campos do `output_schema.json` (`source_link` saiu; o link já vai na linha "Fonte").
- Saídas geradas de verdade pelo Gemini com `src/pipeline/run_adapters.py`, a partir das classificações reais do Router v0.3.1.
- Temperatura 1.0 nos modelos Gemini 3, como recomenda o guia do Google.

### 0.2.0 (21/10/2026)
- "Por que funciona" só aparece se a resposta original explicar o motivo. Na v0.1 essa seção convidava o modelo a inventar.
- Linha "Fonte" com autores e licença (CC BY-SA 4.0 exige atribuição).
- Resposta não aceita é sinalizada como "solução relatada pela comunidade".
- Newsletter não fala em "semana" quando o período não é de uma semana; Dica Rápida leva crédito; regra para "Em alta" quando os tópicos não se repetem.

### 0.1.0 (21/10/2026)
- Rascunho inicial.
