---
Projeto: CommunityLab - Motor Inteligente de Transformação e Distribuição para Comunidades Digitais
Versão: 0.4.1
Autor: Equipe 14 G10
Modelo: Gemini free tier (gemini-3.5-flash-lite ou gemini-3.1-flash-lite) | Groq
Temperatura: 1.0 nos modelos Gemini 3 (recomendação do Google); 0.0 nos demais
Entrada: 1 thread (pergunta/post + respostas) no formato data/schemas/input_schema.json
Formato_saida: JSON (responseMimeType="application/json" no Gemini; response_format={"type":"json_object"} no Groq)
Casos: 32, sendo 17 reais e 15 sintéticos (2 rodadas de testes)
Critério de aceite: 100% dos casos aprovados
Elaborado em: 10/11/2026
---

# Resultados do Benchmark do Router
- **Configurações:** gemini-3.5-flash-lite, temperatura 1.0
- **Execução:** 09/11/26 (1º rodada de testes) | 10/11/26 (2º rodada de testes)
- **Casos:** 32 casos (17 reais e 15 sintéticos)
- **Versão:** 0.4.1

>Relatório gerado a partir das execuções do `eval_router.py`.

## 1. Resumo Executivo:

### 1.1. Rodada de Teste 01 (09/11/26)

| Conjunto         | Acerto | Percentual | Tempo de Execução | Tempo Médio por Requisição | Tokens Consolidados (Entrada) | Tokens Consolidados (Saída) | Tokens Consolidados (Total) | Tokens Consolidados (Média) |
|:-----------------|:-------|:-----------|:------------------|:----------|:----------|:----------|:----------|:--------|
| Dados Reais      | 17/17  | 100%       | 48.18s            | 2.83s     | 76.101    | 3.674     | 79.775    |4.693    |
| Dados Sintéticos | 15/15  | 100%       | 46.19s            | 3.08s     | 42.716    | 2.509     | 45.225    |3.015    |

### 1.2. Rodada de Teste 02 (10/11/26)

| Conjunto         | Acerto | Percentual | Tempo de Execução | Tempo Médio por Requisição | Tokens Consolidados (Entrada) | Tokens Consolidados (Saída) | Tokens Consolidados (Total) | Tokens Consolidados (Média) |
|:-----------------|:-------|:-----------|:------------------|:----------|:----------|:----------|:----------|:--------|
| Dados Reais      | 17/17  | 100%       | 186.24s            | 10.96s     | 76.110    | 3.599    | 79.709    |4.689    |
| Dados Sintéticos | 15/15  | 100%       | 124.61s            | 8.31s     | 47.508    | 2.685     | 50.193    |3.347    |

## 2. Casos Reais por Fonte de Dados:

| Fonte	                         | Casos   | Tipos                                         |
|:-------------------------------|:--------|:----------------------------------------------|
| Stack Overflow/Stack Exchange	 |  10     | perguntas técnicas, respostas aceitas e score |
| Mastodon	                     |   5     | ruído, opinião, idioma e sentimento           |
| Hacker News	                   |   2     | propaganda, debates e análises textuais       |
| **Total**	                     |  **17** |                                               |

## 3. Casos Sintéticos por Fonte de Dados:

| Fonte	                         | Casos      | Tipos                                                       |
|:-------------------------------|:-----------|:------------------------------------------------------------|
| Stack Overflow/Stack Exchange	 |   2        | perguntas técnicas, resposta aceita e pergunta sem resposta |
| Mastodon	                     |  10        | conquistas, depoimento, dúvidas, feedback de curso, debate, ruído, prompt injection e certificação           |
| Hacker News	                   |   3        | relato de sucesso, jailbreak e exposição de PII/secret      |
| **Total**	                     |  **15**    |                                                             |

## 4. Resultado dos Casos Executados

### 4.1. Rodada de Teste 01 (09/11/26)

| Caso de Teste | Conjunto         | Fonte de Dados                | Case                     | Acerto | Tempo de Execução | Tokens Consolidados (Entrada)  | Tokens Consolidados (Saída) | Tokens Consolidados (Total) |
|:-----|:-----------------|:------------------------------|:-------------------------|:-------|:--------------------|:------|:----------|:-----|
| CT01 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_duvida_com_resposta_aceita_llamaindex  | Ok     | 2.11s | 3982| 190 | 4172 |
| CT02 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_duvida_com_resposta_aceita_vscode      | Ok     | 2.19s | 3443| 177 | 3620 |
| CT03 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_duvida_com_resposta_aceita_symfony_ai  | Ok     | 2.29s | 4712| 181 | 4893 |
| CT04 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_resposta_nao_aceita_windsurf           | Ok     | 1.85s | 3339| 186 | 3525 |
| CT05 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_duvida_sem_resposta_muito_vista        | Ok     | 2.39s | 9747| 347 | 10094|
| CT06 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_duvida_sem_resposta_langchain_mcp      | Ok     | 1.91s | 4289| 188 | 4477 |
| CT07 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_limitacao_de_ferramenta_tom_objetivo   | Ok     | 1.87s | 3295| 187 | 3482 |
| CT08 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_desanimo_pessoal_vibe_coder            | Ok     | 2.48s | 3146| 195 | 3341 |
| CT09 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_debate_mercado_com_respostas           | Ok     | 2.09s | 3989| 185 | 4174 |
| CT10 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_pergunta_vaga_ruido                    | Ok     | 2.03s | 3028| 174 | 3202 |
| CT11 | Casos Reais      | Mastodon                      | real_mastodon_bot_politica                     | Ok     | 1.98s | 3565| 173 | 3738 |
| CT12 | Casos Reais      | Mastodon                      | real_mastodon_noticia_ia_rss                   | Ok     | 1.90s | 3250| 187 | 3437 |
| CT13 | Casos Reais      | Mastodon                      | real_mastodon_opiniao_com_link                 | Ok     | 1.86s | 3161| 195 | 3356 |
| CT14 | Casos Reais      | Mastodon                      | real_mastodon_japones_metadado_errado          | Ok     | 11.55s| 9070| 354 | 9424 |
| CT15 | Casos Reais      | Mastodon                      | real_mastodon_opiniao_negativa                 | Ok     | 4.04s | 8215| 405 | 8620 | 
| CT16 | Casos Reais      | Hacker News                   | real_hn_propaganda                             |   Ok   | 2.00s |3006 | 183 | 3189 |
| CT17 | Casos Reais      | Hacker News                   | real_hn_sem_conteudo                           |   Ok   | 1.87s |2864 | 167 | 3031 |
| CT18 | Casos Sintéticos | Sintético (Mastodon)          | conquista_vaga_detalhada                       |   OK   | 1.95s |2842 | 171 | 3013 |
| CT19 | Casos Sintéticos | Sintético (Mastodon)          | conquista_vaga_ingles                          |   OK   | 1.93s |2820 | 178 | 2998 |
| CT20 | Casos Sintéticos | Sintético (SE)                | depoimento_generico                            |   OK   | 1.92s |2797 | 162 | 2959 |
| CT21 | Casos Sintéticos | Sintético (SE)                | duvida_com_resposta_aceita                     |   OK   | 1.91s |2947 | 178 | 3125 |
| CT22 | Casos Sintéticos | Sintético (Mastodon)          | duvida_sem_resposta                            |   OK   | 2.07s |2845 | 173 | 3018 |
| CT23 | Casos Sintéticos | Sintético (Mastodon)          | duvida_frustrada                               |   OK   | 1.93s |2816 | 166 | 2982 |
| CT24 | Casos Sintéticos | Sintético (Mastodon)          | feedback_negativo_curso                        |   OK   | 2.23s |2812 | 168 | 2980 |
| CT25 | Casos Sintéticos | Sintético (Mastodon)          | spam                                           |   OK   | 1.80s |2807 | 143 | 2950 |
| CT26 | Casos Sintéticos | Sintético (Mastodon)          | so_emoji                                       |   OK   | 2.06s |2790 | 157 | 2947 |
| CT27 | Casos Sintéticos | Sintético (Mastodon)          | prompt_injection                               |   OK   | 1.82s |2811 | 151 | 2962 |
| CT28 | Casos Sintéticos | Sintético (Mastodon)          | debate                                         |   OK   | 6.36s |2815 | 169 | 2984 |
| CT29 | Casos Sintéticos | Sintético (Mastodon)          | certificacao                                   |   OK   | 1.97s |2828 | 180 | 3008 |
| CT30 | Casos Sintéticos | Sintético (Hacker News)       | relato_sucesso                                 |   OK   | 1.94s |2948 |179  | 3127 |
| CT31 | Casos Sintéticos | Sintético (Hacker News)       | jailbreaking                                   |   OK   | 1.93s |2887 |164  | 3051 |
| CT32 | Casos Sintéticos | Sintético (Hacker News)       | pii_secret_exposto                             |   OK   | 1.81s |2951 |170  | 3121 |

### 4.2. Rodada de Teste 02 (10/11/26)

#### Casos Reais

| Caso de Teste | Conjunto         | Fonte de Dados                | Case                     | Acerto | Tempo de Execução | Tokens Consolidados (Entrada)  | Tokens Consolidados (Saída) | Tokens Consolidados (Total) |
|:-----|:-----------------|:------------------------------|:-------------------------|:-------|:--------------------|:------|:----------|:-----|
| CT01 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_duvida_com_resposta_aceita_llamaindex  | Ok     | 2.01s | 3982| 178 | 4160 |
| CT02 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_duvida_com_resposta_aceita_vscode      | Ok     | 9.23s | 3443| 191 | 3634 |
| CT03 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_duvida_com_resposta_aceita_symfony_ai  | Ok     | 7.83s | 4712| 153 | 4865 |
| CT04 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_resposta_nao_aceita_windsurf           | Ok     | 5.51s | 3339| 190 | 3529 |
| CT05 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_duvida_sem_resposta_muito_vista        | Ok     | 5.26s | 9756| 359 | 10115|
| CT06 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_duvida_sem_resposta_langchain_mcp      | Ok     | 13.22s | 4289| 150 | 4439 |
| CT07 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_limitacao_de_ferramenta_tom_objetivo   | Ok     | 6.59s | 3295| 186 | 3481 |
| CT08 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_desanimo_pessoal_vibe_coder            | Ok     | 1.93s | 3146| 174 | 3320 |
| CT09 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_debate_mercado_com_respostas           | Ok     | 11.93s | 3989 | 181 | 4170 |
| CT10 | Casos Reais      | Stack Overflow/Stack Exchange | real_se_pergunta_vaga_ruido                    | Ok     | 3.31s | 3028| 190 | 3218 |
| CT11 | Casos Reais      | Mastodon                      | real_mastodon_bot_politica                     | Ok     | 16.83s | 3565| 173 | 3738 |
| CT12 | Casos Reais      | Mastodon                      | real_mastodon_noticia_ia_rss                   | Ok     | 2.67s | 3250| 194 | 3444 |
| CT13 | Casos Reais      | Mastodon                      | real_mastodon_opiniao_com_link                 | Ok     | 8.84s | 3161| 196 | 3357 |
| CT14 | Casos Reais      | Mastodon                      | real_mastodon_japones_metadado_errado          | Ok     | 60.56s| 9069| 349 | 9418 |
| CT15 | Casos Reais      | Mastodon                      | real_mastodon_opiniao_negativa                 | Ok     | 3.82s | 8216| 397 | 8613 | 
| CT16 | Casos Reais      | Hacker News                   | real_hn_propaganda                             |   Ok   | 2.43s |3006 | 170 | 3176 |
| CT17 | Casos Reais      | Hacker News                   | real_hn_sem_conteudo                           |   Ok   | 1.87s |2864 | 167 | 3031 |
| CT18 | Casos Sintéticos | Sintético (Mastodon)          | conquista_vaga_detalhada                       |   OK   | 8.33s |2842 | 178 | 3020 |
| CT19 | Casos Sintéticos | Sintético (Mastodon)          | conquista_vaga_ingles                          |   OK   | 1.92s |2820 | 185 | 3005 |
| CT20 | Casos Sintéticos | Sintético (SE)                | depoimento_generico                            |   OK   | 10.49s |2797 | 153 | 2950 |
| CT21 | Casos Sintéticos | Sintético (SE)                | duvida_com_resposta_aceita                     |   OK   | 14.97s |2947 | 170 | 3117 |
| CT22 | Casos Sintéticos | Sintético (Mastodon)          | duvida_sem_resposta                            |   OK   | 2.37s |2845 | 170 | 3015 |
| CT23 | Casos Sintéticos | Sintético (Mastodon)          | duvida_frustrada                               |   OK   | 5.29s |2816 | 173 | 2989 |
| CT24 | Casos Sintéticos | Sintético (Mastodon)          | duvida_frustrada                               |   OK   | 2.17s |2812 | 171 | 2983 |
| CT25 | Casos Sintéticos | Sintético (Mastodon)          | spam                                           |   OK   | 9.27s |2807 | 152 | 2959 |
| CT26 | Casos Sintéticos | Sintético (Mastodon)          | so_emoji                                       |   OK   | 3.07s |2790 | 148 | 2938 |
| CT27 | Casos Sintéticos | Sintético (Mastodon)          | prompt_injection                               |   OK   | 1.82s |2811 | 155 | 2966 |
| CT28 | Casos Sintéticos | Sintético (Mastodon)          | debate                                         |   OK   | 14.01s |2815 | 177 | 2992 |
| CT29 | Casos Sintéticos | Sintético (Mastodon)          | certificacao                                   |   OK   | 2.30s |2828 | 181 | 3009 |
| CT30 | Casos Sintéticos | Sintético (Hacker News)       | relato_sucesso                                 |   OK   | 7.84s |2948 |181  | 3129 |
| CT31 | Casos Sintéticos | Sintético (Hacker News)       | jailbreaking                                   |   OK   | 2.35s |2887 |168  | 3055 |
| CT32 | Casos Sintéticos | Sintético (Hacker News)       | pii_secret_exposto                             |   OK   | 38.41s |7743 |323  | 8066 |

---

## 5. Conclusão

Os testes atenderam com êxito ao critério de aceite do benchmark, alcançando **100% de aprovação** nos casos esperados.

Durante o Teste 02, foram identificadas requisições com status HTTP 503, possivelmente relacionadas à limitação ou à instabilidade do provedor, tanto no conjunto de dados reais quanto no sintético. Essas ocorrências, entretanto, não impediram a conclusão das execuções nem comprometeram o resultado do benchmark.

**Resultados:** 
- **CT05** (`real_se_duvida_sem_resposta_muito_vista`) teve o maior consumo de tokens nas duas rodadas: **10094 tokens** e **10115 tokens**, respectivamente.
- **CT14** (`real_mastodon_japones_metadado_errado`) e **CT15** (`real_mastodon_opiniao_negativa `) consumiram entre **8000** e **9500 tokens** nas duas rodadas de teste.
- **CT32** (`pii_secret_exposto`) consumiu **3121 tokens** na primeira rodada e **8066 tokens** na segunda rodada.
- Os demais casos de testes consumiram entre **2900** e **5000 tokens** por requisição.

**Causas prováveis:**
- **CT05:** contém uma pergunta do Stack Overflow muito extensa, com logs, HTML e um bloco grande de código PHP. Mesmo a primeira chamada já exige muito contexto.

- **CT14:** contém HTML do Mastodon, várias URLs, hashtags e texto japonês. URLs, marcações HTML e conteúdo multilíngue podem aumentar a quantidade de tokens.

- **CT15:** possui um texto relativamente longo em inglês, citações, formatação HTML e link externo. Além disso, é um caso limítrofe entre opinião, debate e moderação.

- **CT05** (`real_se_duvida_sem_resposta_muito_vista`), **CT14** (`real_mastodon_japones_metadado_errado`) e **CT15** (`real_mastodon_opiniao_negativa `) já eram outliers na primeira rodada (09/11), com praticamente os mesmos tokens. Isso confirma que o tamanho/complexidade dos payloads é estrutural.

- **CT32:** o payload é curto, então o tamanho do conteúdo não explica os **8.066 tokens**. Trata-se de um caso sintético de segurança com PII e credencial. O CT32 mudou de **3.111 tokens** e **sem retry** no teste 01 (09/11) para **8.066 tokens** e **com retry** no teste 02 (10/11). Logo, CT32 demonstra claramente que a variação veio da execução adicional com retry, provavelmente por erro de validação ou instabilidade do provedor. 

**Análise de Consumo de Tokens:**
- Considerando o consumo médio de tokens por requisição nos 17 casos reais do Teste 01 (total de **79.775 tokens** e média de **4.693 tokens**) — e do Teste 02 (total de **79.709 tokens** e média de **4.689 tokens**), estima-se que, dentro da cota diária considerada para um modelo com plano gratuito, como o `gemini-3.5-flash-lite`, seja possível processar até **204 requisições por dia** sem esgotar essa cota.

>[!NOTE] Essa estimativa considera o consumo médio observado nos testes e deve ser interpretada como uma referência, pois o limite efetivo pode variar conforme as políticas do provedor, a forma de contabilização dos tokens e os demais limites do plano. 

**Avisos**
* Rota sugerida pelo modelo diferente da rota das regras que podem ser ajustadam no n8n:
   * CT32 (`pii_secret_exposto`): modelo sugeriu 'moderation', as regras dão 'discard' (o n8n corrige)
