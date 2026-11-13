---
Projeto: CommunityLab - Motor Inteligente de Transformação e Distribuição para Comunidades Digitais
Versão: 0.4.0
Autor: Equipe 14 G10
Modelo: Gemini free tier (gemini-3.5-flash-lite ou gemini-3.1-flash-lite) | Groq
Temperatura: 1.0 nos modelos Gemini 3 (recomendação do Google); 0.0 nos demais
Entrada: saída do Router (rota success_case ou faq) + item original
Formato_saida: JSON compatível com um item de suggested_content (data/schemas/output_schema.json)
Jobs: 9 (2 rodadas de testes)
Critério de aceite: 100% dos casos aprovados
Elaborado em: 13/11/2026
---

# Resultados do Benchmark do Adapter
- **Configurações:** gemini-3.5-flash-lite, temperatura 1.0
- **Execução:** 12/11/2026 e 13/11/2026 (2 Rodadas de Teste)
- **Jobs:** 9
- **Versão:** 0.4.0

>Relatório gerado a partir das execuções do `eval_adapters.py`.

## 1. Resumo Executivo:

### 1.1. Execução do Teste 01 
- **Data da Execução:** 12/11/2026
- **Período:** 22:24:06 (UTC-3)

| Canais        | Acerto | Percentual | Tempo de Execução | Tempo Médio por Requisição | Tokens Consolidados (Entrada) | Tokens Consolidados (Saída) | Tokens Consolidados (Total) | Tokens Consolidados (Média) |
|:-----------------|:-------|:-----------|:------------------|:----------|:----------|:----------|:----------|:--------|
| Social/FAQ/Newsletter  | 9/9  | 100%       | 26.02s            | 2.89s     | 20.043    | 2.342     | 22.385    |2.488   |

**Saídas do modelo:** `data/prompts/outputs/adapters_gemini_20261112-2224.json`.

### 1.2. Execução do Teste 02 
- **Data da Execução:** 13/11/2026
- **Período:** 10:39:15 (UTC-3)

| Canais        | Acerto | Percentual | Tempo de Execução | Tempo Médio por Requisição | Tokens Consolidados (Entrada) | Tokens Consolidados (Saída) | Tokens Consolidados (Total) | Tokens Consolidados (Média) |
|:-----------------|:-------|:-----------|:------------------|:----------|:----------|:----------|:---------|:--------|
| Social/FAQ/Newsletter  | 9/9  | 100%       | 22.60s        | 2.51s     | 19.517   | 1.964     | 21.481    |2.387   |

**Saídas do modelo:** `data/prompts/outputs/adapters_gemini_20261113-1039.json`.

---

  "average_duration_seconds": 2.511,
  "total_duration_seconds": 22.599,
  "ran_at": "2026-11-13T10:39:15",
  "token_usage": {
    "prompt_tokens": 19517,
    "completion_tokens": 1964,
    "total_tokens": 21481
  },

## 2. Casos por Canais:

| Canais	                         | Casos   | Tipos                                         |
|:-------------------------------|:--------|:----------------------------------------------|
| linkedin	                      |  2     | conquista e dica técnica |
| mastodon	                     |   1     | conquista        |
| x/twitter	                   |   2     | conquista e dica técnica       |
| faq	                   |   3    | respostas aceitas e sem resposta      |
| newsletter	                   |   10 (1 lote)    | Lote com perguntas técnicas, respostas aceitas e score       |

| **Total**	                     |  **9** |                                     

---

## 4. Resultado dos Casos Executados

### 4.1. Execução do Teste 01

| Caso de Teste | Canal         | Itens de Origem                | Case                     | Acerto | Tempo de Execução | Tokens Consolidados (Entrada)  | Tokens Consolidados (Saída) | Tokens Consolidados (Total) |
|:-----|:-----------------|:------------------------------|:-------------------------|:-------|:--------------------|:------|:----------|:-----|
| CT01 | linkedin | t01 | linkedin_conquista_sintetica | Ok | 5.10s | 1874 | 409 | 2283 |
| CT02 | linkedin | se-79838505 | linkedin_dica_tecnica_real | Ok | 2.69s | 2723 | 211 | 2934 |
| CT03 | x/twitter | t02 | x_conquista_sintetica | Ok | 2.15s | 1232 | 81 | 1313 |
| CT04 | x/twitter | se-79998781 | x_dica_tecnica_real | Ok | 1.96s | 1856 | 114 | 1970 |
| CT05 | mastodon | t12 | mastodon_certificacao_sintetica | Ok | 1.96s | 1285 | 95 | 1380 |
| CT06 | faq | se-79998781 | faq_resposta_aceita_vscode_real | Ok | 2.48s | 1522 | 306 | 1828 |
| CT07 | faq | se-79857625 | faq_resposta_aceita_symfony_real | Ok | 5.15s | 3318 | 683 | 4001 |
| CT08 | faq | se-79837611 | faq_sem_resposta_ollama_real | Ok | 1.75s | 2031 | 74 | 2105 |
| CT09 | newsletter | se-79838505, se-79998781, se-79857625, se-79850130, se-79837611,  se-79935672, se-79958777, se-79874274, se-79835621, mst-117476661482589915 | newsletter_lote_real | Ok | 2.78s | 4202 | 369 | 4571 |

### 4.2. Execução do Teste 02

| Caso de Teste | Canal         | Itens de Origem                | Case                     | Acerto | Tempo de Execução | Tokens Consolidados (Entrada)  | Tokens Consolidados (Saída) | Tokens Consolidados (Total) |
|:-----|:-----------------|:------------------------------|:-------------------------|:-------|:--------------------|:------|:----------|:-----|
| CT01 | linkedin | t01 | linkedin_conquista_sintetica |  Ok  |  5.08s  |  1873  |  426  |  2299 |
| CT02 | linkedin | se-79838505 | linkedin_dica_tecnica_real |  Ok  |  2.19s  |  2723  |  218  |  2941 |
| CT03 | x/twitter | t02 | x_conquista_sintetica |  Ok  |  1.75s  |  1232  |  84  |  1316 |
| CT04 | x/twitter | se-79998781 | x_dica_tecnica_real |  Ok  |  1.80s  |  1856  |  117  |  1973 |
| CT05 | mastodon | t12 | mastodon_certificacao_sintetica |  Ok  |  2.09s  |  1285  |  95  |  1380 |
| CT06 | faq | se-79998781 | faq_resposta_aceita_vscode_real |  Ok  |  2.82s  |  1522  |  258  |  1780 |
| CT07 | faq | se-79857625 | faq_resposta_aceita_symfony_real |  Ok  |  2.39s  |  2793  |  305  |  3098 |
| CT08 | faq | se-79837611 | faq_sem_resposta_ollama_real |  Ok  |  1.88s  |  2031  |  73  |  2104 |
| CT09 | newsletter | se-79838505, se-79998781, se-79857625, se-79850130, se-79837611,  se-79935672, se-79958777, se-79874274, se-79835621, mst-117476661482589915 | newsletter_lote_real |  Ok  |  2.60s  |  4202  |  388  |  4590 |

---

## 5. Conclusão

As execuções finais do benchmark atenderam com êxito aos critérios de aceite do sistema, alcançando **100% de aprovação (9/9 jobs)** em ambas as rodadas de teste com o modelo `gemini-3.5-flash-lite`.

Durante o ciclo de validação e refinamento que antecedeu a consolidação da versão `0.4.0` dos adapters de faq/newsletter e social, observou-se:

* **Resiliência a Instabilidades de API:** Foram registradas instabilidades pontuais com retornos HTTP 503 do provedor, contornadas com sucesso pelo cliente HTTP resiliente e pelas estratégias de novas tentativas (*retries*).

* **Ajustes de Robustez e Correção de Casos:**
    * `faq_sem_resposta_ollama_real`: O modelo lidou corretamente com o cenário limite, injetando a tag `[PRECISA DE REVISÃO TÉCNICA]` no corpo e validando o comportamento esperado.
    * `faq_resposta_aceita_symfony_real`: Casos iniciais falharam por ausência da seção obrigatória `**Resposta curta:**`. O problema foi mitigado com o endurecimento do prompt em `adapter_faq.md` (reforçando a proibição de sinônimos como `**Resposta:**` ou `**Explicação:**`) e com validações dedicadas no `adapters_validator.py`.
    * `linkedin_conquista_sintetica`: Apresentou estouramentos esporádicos no limite de hashtags (gerando 7 quando o teto era 5). O comportamento foi normalizado com regras de correção integradas ao `adapters_prompt_builder.py` e validações de contagem no `adapters_validator.py`.

**Principais Insights:**

* **CT09** (`newsletter_lote_real`) registrou o maior consumo de tokens nas duas rodadas: **4.571 tokens** (Teste 01) e **4.590 tokens** (Teste 02).
* **CT07** (`faq_resposta_aceita_symfony_real`) ficou logo atrás, apresentando um consumo expressivo de **4.001 tokens** (Teste 01) e **3.098 tokens** (Teste 02).

**Causas prováveis:**

* **CT09:** O processamento agrupa um lote com múltiplos itens de origem em uma única chamada, gerando um payload de contexto consideravelmente maior.
* **CT07:** O alto consumo reflete tanto o volume extenso da thread técnica original do Stack Overflow quanto o custo adicional de tokens gerado pelo acionamento do ciclo de auto-correção (*retry*) durante o endurecimento da validação da seção `**Resposta curta:**`.

**Análise de Consumo de Tokens:**

* Considerando o consumo global das execuções (média aproximada de **22.300 tokens totais** distribuídos em **9 jobs por rodada**), o custo médio por job individual fica em torno de **2.480 tokens**.

* Separando por complexidade, os adapters de redes sociais e FAQ unitário operam na faixa de **1.300 a 2.100 tokens por requisição**, enquanto o lote de newsletter atinge patamares próximos a **4.600 tokens**.

* Com base nesses patamares e considerando as cotas de modelos leves voltados para desenvolvimento (como o `gemini-3.5-flash-lite`), estima-se que uma operação diária estruturada com picos de até 100 execuções mistas (divididas entre posts sociais, FAQs e lotes de newsletter) consome uma fração segura da cota diária permitida, garantindo estabilidade operacional sem esgotar limites de taxa (*rate limits*).

>[!NOTE]
>Esta estimativa considera o comportamento médio observado em ambiente de testes e serve como referência arquitetural. Os limites efetivos em produção dependem das políticas vigentes do provedor, janelas de RPM/TPM (*Requests/Tokens Per Minute*) e regras específicas do plano contratado.