# Dicionário de dados e fluxo de execução do n8n

O projeto coleta dados de Stack Exchange, Mastodon e Hacker News, guarda os resultados brutos na OCI e classifica os registros para triagem editorial. Este mapa descreve as exportações versionadas e os consumidores identificados no código. O estado de publicação e as execuções no servidor precisam de confirmação no ambiente n8n.

| Workflows | Fluxo |
| --- | --- |
| WF02–04, WF08 | Coleta de perguntas, licenças e respostas em fluxos distintos. O WF08 lê os arquivos da OCI e consolida os registros. |
| WF05 | Lista objetos por pasta, baixa os arquivos e devolve um ZIP. |
| WF06–07 | Coleta por hashtag no Mastodon ou por consulta no Hacker News. |
| WF09–11 | Selecionam e leem arquivos brutos por fonte e tópico, classificam o conteúdo e salvam os resultados. |
| WF12 | Expõe a consulta de um arquivo processado por fonte e tag. Não foi encontrada chamada ao endpoint no código versionado do Streamlit. |
| WF13 | Recebe a pergunta e o contexto do painel de sentimento pelo serviço de chat do Streamlit. |

## Fluxo entre a coleta, a triagem e o aplicativo

Os webhooks são acionados separadamente. A integração entre coleta e triagem ocorre pelos arquivos na OCI.

| Fonte | Caminho dos dados | Unidade avaliada |
| --- | --- | --- |
| [Stack Overflow](specs/api-stackexchange.md) | WF02, WF03 e WF04 gravam perguntas, licenças e respostas em `collected/sample_*`, preservando a tag. WF08 lê de `collected/`, agrupa por `source_id` e grava `raw/stackoverflow_<tag>.json`. | WF10 lê o consolidado escolhido por `tag`. O `limit` (padrão 1) controla perguntas, e a classificação é por resposta. |
| [Mastodon](specs/api-mastodon.md) | WF06 consulta duas instâncias e grava `raw/mastodon_<tag>.json`. WF09 seleciona pela tag do POST. | Publicação com limpeza de HTML. O limite padrão é 50. |
| [Hacker News](specs/api-hackernews.md) | WF07 busca no Algolia, consulta publicações e comentários diretos na Firebase e grava em `raw/`. WF11 recebe `tag` e `limit` no POST e retorna 400 para entrada inválida. | Comentário com texto, avaliado com o contexto da publicação. |

A triagem grava o resultado principal em `processed/` e os lotes de destino em `processed/routing/`. O Streamlit tem um fluxo de download de pasta pelo WF05 e uma tela que lê arquivos processados. O WF05 aceita `query.folder` (padrão `processed/`), valida o caminho relativo e devolve um ZIP, ou HTTP 400 para pasta inválida e 404 quando não encontra objetos. O WF13 usa o contexto do painel e o histórico enviados pelo aplicativo.

O WF03 e o WF08 consultam `social_topic` no gatilho manual. As chamadas por webhook usam o parâmetro `tagged` recebido no corpo e pulam a consulta à tabela. O [mapa de credenciais](specs/n8n-credentials.md) lista os caminhos dos webhooks.

## Convenções

- Os nomes dos arquivos de workflow começam com `wfNN_`. Os caminhos de webhook seguem a configuração de cada exportação, com hífens e, em alguns casos, sublinhados.
- Os campos do projeto usam principalmente `snake_case`, como `source_id`, `suggested_route` e `needs_human_review`. Os campos de fornecedores preservam a grafia de origem, como `objectID` no Algolia e `Key` na API compatível com S3. O n8n também expõe `statusCode` e `chatInput` nos pontos indicados.
- Os itens do n8n trafegam como JSON. Arquivos baixados ou gerados passam pela parte binária do item, normalmente `binary.data`. As conversões e extrações abaixo marcam essa transição.
- Para o WF12, `source` é uma string com um dos valores `stackoverflow`, `mastodon` ou `hackernews`. `tag` é uma string de até 200 caracteres, começa com letra ou número e admite também ponto, `+`, `#`, `_`, `;` e hífen. A grafia é preservada na chave `processed/result_<source>_<tag>.json`.
- Nos fluxos de triagem, a revisão humana tem precedência sobre o roteamento editorial. As rotas reconhecidas são `success_case`, `faq`, `newsletter_only`, `moderation` e `discard`, com uma saída de fallback. O WF09 lê a decisão em `editorial`. Os WF10 e WF11 leem os campos equivalentes na raiz.

## Campos compartilhados e contratos de consumo

| Campo | Tipo e uso |
| --- | --- |
| `tagged` | String de busca dos coletores Stack Overflow e de seleção no WF08. Compõe o nome dos três arquivos em `collected/` e do consolidado em `raw/`. |
| `tag`, `limit` | Tema e número de itens a triar. A unidade do limite é publicação no WF09, pergunta no WF10 e comentário no WF11. |
| `source_id`, `answer_id` | Identificador da pergunta usado na junção do WF08 e identificador da resposta preservado na triagem do Stack Overflow. |
| `post_id`, `comment.id`, `source_file` | Identificador da publicação no Mastodon, identificador do comentário no Hacker News e chave do objeto bruto que alimentou a triagem. |
| `sentiment`, `strength`, `confidence` | Categoria de sentimento, intensidade e confiança da classificação. As escalas numéricas de intensidade e confiança vão de 0 a 1. |
| `suggested_route`, `needs_human_review`, `routing` | Rota editorial sugerida, decisão de revisão humana e metadados do encaminhamento aplicado. |

### Endpoints do painel

| Workflow | Entrada | Resultado |
| --- | --- | --- |
| WF12 | Query `source` e `tag` conforme as regras acima. | 200 com `success`, `statusCode`, `source`, `tag`, `object_key`, `count` e `items` (array). 400 com `INVALID_QUERY`, 404 com `PROCESSED_FILE_NOT_FOUND` ou 502 com `STORAGE_DOWNLOAD_FAILED` / `INVALID_PROCESSED_DATA`. |
| WF13 | Corpo com `request_id`, `session_id`, `question`, `context` e `history` opcional. O contexto inclui `snapshot_id`, `loaded_at`, `filters`, `metrics.unique_interactions`, `evidence` e `limitations`. | 200 com `request_id`, `snapshot_id`, `status` e `answer`. 400 por entrada inválida ou 502 por falha ou resposta vazia do agente. |

No WF13, perguntas de ranking por tema podem ser respondidas diretamente com as métricas do contexto. As demais seguem para o agente. O WF13 aceita até 12 mensagens no histórico, com `role` igual a `user` ou `assistant` e `content` textual. O contexto aceita até 30 evidências e exige uma contagem inteira e não negativa em `metrics.unique_interactions`. O limite do corpo serializado é de 200.000 caracteres.

## Como ler as tabelas

Na coluna **Dados e regras**, setas indicam atribuições ou mudança de representação. Nos nós de código, os campos lidos ou construídos registram o contrato observável no JavaScript. A coluna **Conexões** distingue saídas condicionais, saídas de erro e conexões auxiliares de IA quando declaradas no JSON. Os links apontam para as exportações versionadas.


## wf02_coleta-stack-exchange-questions-integrada

[wf02_coleta-stack-exchange-questions-integrada.json](../n8n/workflows/wf02_coleta-stack-exchange-questions-integrada.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `When clicking ‘Execute workflow’` | Disparo manual, sem campos de requisição | `Define Search parameters` |
| `HTTP Request` | `https://api.stackexchange.com/2.3/questions`. Query: `site` → `$json.site`, `pagesize` → `$json.pagesize`, `order` → `desc`, `sort` → `votes`, `tagged` → `$json.tagged`, `filter` → `!*Mg4PjfqKhwRM7nE`, `fromdate` → `$json.fromdate`. Emite resposta da API | `Split Out` |
| `Split Out` | `items` → um item por elemento | `Standard Questions` |
| `Upload a file` | `binary.data` → objeto OCI `'collected/' + $binary.data.fileName` | `Respond to Webhook` |
| `Webhook` | `POST /webhook/wf02-coleta-stack-exchange` → `headers`, `params`, `query`, `body` (Header Auth) | `Define Search parameters` |
| `Respond to Webhook` | HTTP `200` → `{ "status": "success", "message": "Coleta de perguntas concluída e arquivo disponibilizado no bucket OCI." }` | Fim |
| `Define Search parameters` | `tagged` (string) ← `$json.body?.tagged ?? 'langsmith'`, `fromdate` (number) ← `Number($json.body?.fromdate ?? 1760929200)`, `pagesize` (number) ← `Number($json.body?.pagesize ?? 100)`, `site` (string) ← `$json.body?.site ?? 'stackoverflow'` | `Validade Research parameters` |
| `Validade Research parameters` | Valida `tagged`, `site`, `fromdate` e `pagesize`. Preserva os parâmetros e emite `_validation.valid` e `_validation.message` | `Valid?` |
| `Valid?` | `$json._validation.valid` true | Verdadeiro → `HTTP Request` · Falso → `Validation Error return` |
| `Validation Error return` | HTTP `400` → `{ status: "error", message: "Parâmetros de busca inválidos.", details: $json._validation.message }` | Fim |
| `Standard Questions` | `source_id` (string) ← `$json.question_id`, `owner_question` (string) ← `$json.owner.display_name`, `title_question` (string) ← `$json.title`, `body_question` (string) ← `$json.body`, `link_question` (string) ← `$json.link`, `tags` (array) ← `$json.tags`, `score_question` (number) ← `$json.score`, `creation_date_question` (number) ← `$json.creation_date`, `last_activity_date_question` (number) ← `$json.last_activity_date`, `is_answered_question` (boolean) ← `$json.is_answered`, `answer_count_question` (number) ← `$json.answer_count`, `accepted_answer_id_question` (number) ← `$json.accepted_answer_id`, `view_count_question` (number) ← `$json.view_count`, `comment_count_question` (number) ← `$json.comment_count` | `Sanitize and Validate Questions` |
| `Sanitize and Validate Questions` | Lê `input.all`, `item.json`. Constrói ou declara `json`, `source_id`, `owner_question`, `title_question`, `link_question` | `Create Question JSON file` |
| `Create Question JSON file` | Itens JSON → `binary.data` com nome `"sample_" + $('Define Search parameters').item.json.site + "-questions_" + $('Define Search parameters').item.json.tagged + ".json"` | `Upload a file` |

## wf03_coleta-stack-exchange-licenses-integrada

[wf03_coleta-stack-exchange-licenses-integrada.json](../n8n/workflows/wf03_coleta-stack-exchange-licenses-integrada.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `When clicking ‘Execute workflow’` | Disparo manual, sem campos de requisição | `Get Tag` |
| `HTTP Request` | `https://api.stackexchange.com/2.3/questions`. Query: `site` → `$json.site`, `pagesize` → `$json.pagesize`, `order` → `desc`, `sort` → `votes`, `tagged` → `$json.tagged`, `filter` → `!4(sMnI809SBP8*2*0`, `fromdate` → `$json.fromdate`. Emite resposta da API | `Split Out` |
| `Split Out` | `items` → um item por elemento | `Padronizar Licencas` |
| `Upload a file` | `binary.data` → objeto OCI `"collected/" + $binary.data.fileName` | `Loop Over Items` |
| `Definir Parâmetros de Busca` | `tagged` (string) ← `$prevNode.name === 'Get Tag' ? $json.tag : ($json.body?.tagged ?? 'langsmith')`, `fromdate` (number) ← `Number($json.body?.fromdate ?? 1760929200)`, `pagesize` (number) ← `Number($json.body?.pagesize ?? 100)`, `site` (string) ← `$json.body?.site ?? 'stackoverflow'` | `Validar Parâmetros de Busca` |
| `Webhook` | `POST /webhook/wf03-coleta-stack-exchange-licenses` → `headers`, `params`, `query`, `body` (Header Auth) | `Definir Parâmetros de Busca` |
| `Respond to Webhook` | HTTP `200` → `{ "status": "success", "message": "Coleta de licenças concluída e arquivo disponibilizado no bucket OCI." }` | Fim |
| `Validar Parâmetros de Busca` | Valida `tagged`, `site`, `fromdate` e `pagesize`. Preserva os parâmetros e emite `_validation.valid` e `_validation.message` | `Parâmetros Válidos?` |
| `Parâmetros Válidos?` | `$json._validation.valid` true | Verdadeiro → `Loop Over Items` · Falso → `Responder Erro de Validação` |
| `Responder Erro de Validação` | HTTP `400` → `{ status: "error", message: "Parâmetros de busca inválidos.", details: $json._validation.message }` | Fim |
| `Sanitizar e Validar Licencas` | Lê `source_id` e `content_license_question`. Emite `conteudoBase64` com o array JSON, inclusive vazio | `Gerar JSON de Licencas` |
| `Gerar JSON de Licencas` | `conteudoBase64` → `binary.data` com nome `"sample_" + $('Loop Over Items').first(1, $runIndex).json.site + "-licenses_" + $('Loop Over Items').first(1, $runIndex).json.tagged + ".json"` | `Upload a file` |
| `Loop Over Items` | Itera sobre os itens em lotes de `1` | Concluído → `Respond to Webhook` · Iteração → `HTTP Request` |
| `Get Tag` | Lê `social_topic` em ordem de `id` e usa `tag` nas iterações | `Definir Parâmetros de Busca` |
| `Padronizar Licencas` | `source_id` (string) ← `$json.question_id`, `content_license_question` (string) ← `$json.content_license` | `Sanitizar e Validar Licencas` |
| `Sticky Note` | Nota de documentação no editor | Fim |

## wf04_coleta-stack-exchange-answer-integrada

[wf04_coleta-stack-exchange-answer-integrada.json](../n8n/workflows/wf04_coleta-stack-exchange-answer-integrada.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `When clicking ‘Execute workflow’` | Disparo manual, sem campos de requisição | `Define Search Parameters` |
| `Upload a file` | `binary.data` → objeto OCI `"collected/" + $binary.data.fileName` | `Respond to Webhook` |
| `Webhook` | `POST /webhook/wf04-coleta-stack-exchange-answers` → `headers`, `params`, `query`, `body` (Header Auth) | `Define Search Parameters` |
| `Respond to Webhook` | HTTP `200` → `{ "status": "success", "message": "Coleta de perguntas concluída e arquivo disponibilizado no bucket OCI." }` | Fim |
| `Responder Erro de Validação` | HTTP `400` → `{ status: "error", message: "Parâmetros de busca inválidos.", details: $json._validation.message }` | Fim |
| `HTTP Request Answer` | `=https://api.stackexchange.com/2.3/questions/{{ $json.question_ids.join(';') }}/answers`. Query: `site` → `stackoverflow`, `pagesize` → `$('Definir Parâmetros de Busca').first().json.pagesize`, `order` → `desc`, `sort` → `votes`, `filter` → `!22ZfkjB)cHWox5_J4ABtT`. Emite resposta da API | `Split Out Answer` |
| `HTTP Request Question` | `https://api.stackexchange.com/2.3/questions`. Query: `site` → `$json.site`, `pagesize` → `$json.pagesize`, `order` → `desc`, `sort` → `votes`, `tagged` → `$json.tagged`, `filter` → `!*Mg4PjfqKhwRM7nE`, `fromdate` → `$json.fromdate`. Emite resposta da API | `Split Out Question` |
| `Edit question_id` | `question_id` (number) ← `$json.question_id` | `Create question_ids list` |
| `Edit Answer parameters` | `={{ "owner_answer_" + ($json.owner.account_id ?? 'unknown') }}` (object) ← `$json.owner`, `={{ "comment_count_answer_" + ($json.owner.account_id ?? 'unknown') }}` (number) ← `$json.comment_count`, `={{ "down_vote_count_answer_" + ($json.owner.account_id ?? 'unknown') }}` (number) ← `$json.down_vote_count`, `={{ "up_vote_count_answer_" + ($json.owner.account_id ?? 'unknown') }}` (number) ← `$json.up_vote_count`, `={{ "is_accepted_answer_" + ($json.owner.account_id ?? 'unknown') }}` (boolean) ← `$json.is_accepted`, `={{ "score_answer_" + ($json.owner.account_id ?? 'unknown') }}` (number) ← `$json.score`, `={{ "last_activity_date_answer_" + ($json.owner.account_id ?? 'unknown') }}` (number) ← `$json.last_activity_date`, `={{ "creation_date_answer_" + ($json.owner.account_id ?? 'unknown') }}` (number) ← `$json.creation_date`, `answer_id` (number) ← `$json.answer_id`, `source_id` (number) ← `$json.question_id`, `={{ "content_license_answer_" + ($json.owner.account_id ?? 'unknown') }}` (string) ← `$json.content_license`, `={{ "link_answer_" + ($json.owner.account_id ?? 'unknown') }}` (string) ← `$json.link`, `={{ "title_answer_" + ($json.owner.account_id ?? 'unknown') }}` (string) ← `$json.title`, `={{ "body_answer_" + ($json.owner.account_id ?? 'unknown') }}` (string) ← `$json.body` | `Sanitize and Validade Answers` |
| `Create question_ids list` | Lê `input.all`, `item.json.question_id`. Constrói ou declara `json`, `question_ids` | `HTTP Request Answer` |
| `Sanitize and Validade Answers` | Lê `input.all`, `item.json`. Constrói ou declara `source_id`, `json` | `Create Answer JSON file` |
| `Create Answer JSON file` | Itens JSON → `binary.data` com nome `"sample_" + $('Validade Search Parameters').first().json.site + "-answers_" + $('Validade Search Parameters').first().json.tagged + ".json"` | `Upload a file` |
| `Split Out Question` | `items` → um item por elemento | `Edit question_id` |
| `Split Out Answer` | `items` → um item por elemento | `Edit Answer parameters` |
| `Check Valid Parameters` | `$json._validation.valid` true | Verdadeiro → `HTTP Request Question` · Falso → `Responder Erro de Validação` |
| `Validade Search Parameters` | Campos referenciados:  | `Check Valid Parameters` |
| `Define Search Parameters` | `tagged` (string) ← `$json.body?.tagged ?? 'langsmith'`, `fromdate` (number) ← `Number($json.body?.fromdate ?? 1760929200)`, `pagesize` (number) ← `Number($json.body?.pagesize ?? 100)`, `site` (string) ← `$json.body?.site ?? 'stackoverflow'` | `Validade Search Parameters` |

## wf05_download-bucket-OCI

[wf05_download-bucket-OCI.json](../n8n/workflows/wf05_download-bucket-OCI.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `When clicking ‘Execute workflow’` | Disparo manual, sem campos de requisição | `Edit Fields` |
| `Get many files` | Lista `$json.folder` → `Key` e metadados | `Files Found` |
| `Aggregate` | Agrega itens em `data_list` | `ZIP files` |
| `ZIP files` | `={{ Object.keys($binary).join() }}` → ZIP binário | `Return with ZIP file` |
| `Return with ZIP file` | HTTP `200` → `binary` | Fim |
| `Download a file` | `$json.Key` → `binary.data` | `Aggregate` |
| `Webhook` | `GET /webhook/wf05-download-bucket-OCI` → `headers`, `params`, `query`, `body` (Header Auth) | `Edit Fields` |
| `Edit Fields` | `folder` (string) ← `$json.query?.folder ?? $json.folder ?? 'processed/'` | `Validate Folder` |
| `Validate Folder` | Lê `input.all`, `item.json.folder`, `item.json`. Constrói ou declara `json`, `valid`, `statusCode`, `error`, `pairedItem`, `item`, `folder` | `Folder Is Valid` |
| `Folder Is Valid` | `$json.valid` true | Verdadeiro → `Get many files` · Falso → `Return Invalid Folder` |
| `Return Invalid Folder` | HTTP `400` → `{ success: false, statusCode: 400, error: $json.error, message: $json.message }` | Fim |
| `Files Found` | `$json.Key` notEmpty | Verdadeiro → `Download a file` · Falso → `Return Folder Empty` |
| `Return Folder Empty` | HTTP `404` → `{ success: false, statusCode: 404, error: 'FOLDER_EMPTY_OR_NOT_FOUND', message: 'Nenhum arquivo encontrado na pasta informada.', folder: $('Validate Folder').first().json.folder }` | Fim |

## wf06_coleta-mastodon

[wf06_coleta-mastodon.json](../n8n/workflows/wf06_coleta-mastodon.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `When clicking ‘Execute workflow’` | Disparo manual, sem campos de requisição | `Prepare Search Parameter` |
| `Unify Mastodon Posts` | Concatena os itens recebidos | `Consolidar resultados` |
| `Standard Mastodon - Social Posts` | Constrói ou declara `source`, `author`, `text`, `tags`, `media_urls` | `Status - mastodon.social` |
| `Upload a file` | `binary.data` → objeto OCI `'raw/' + $binary.data.fileName` | `Respond to Webhook` · Erro → `OCI Upload Error Response` |
| `Convert to File` | Itens JSON → `binary.data` com nome `'mastodon_' + $('Prepare Search Parameter').first().json.tag + '.json'` | `Upload a file` |
| `Webhook` | `POST /webhook/wf06-coleta-mastodon` → `headers`, `params`, `query`, `body` (Header Auth) | `Prepare Search Parameter` |
| `Respond to Webhook` | HTTP `200` → `{ success: true, status: $('Consolidar resultados').first().json.status, message: $('Consolidar resultados').first().json.status === 'partial_success' ? 'Coleta parcialmente concluída. Os posts da fonte disponível foram armazenados no bucket OCI communitylab-assets.' : 'Coleta concluída. Os posts foram armazenados no bucket OCI communitylab-assets.', total_posts: $('Consolidar resultados').first().json.total_posts, successful_sources: $('Consolidar resultados').first().json.successful_sources, failed_sources: $('Consolidar resultados').first().json.failed_sources }` | Fim |
| `OCI Upload Error Response` | HTTP `502` → `={ "success": false, "error": "oci_storage_failed", "message": "A coleta foi iniciada, mas o arquivo não pôde ser armazenado no bucket OCI communitylab-assets. Verifique a conexão e as credenciais do Object Storage antes de tentar novamente." }` | Fim |
| `If` | `$json.total_posts` gt `0` | Verdadeiro → `Convert to File` · Falso → `Respond - No Posts` |
| `Status - mastodon.social` | Lê `input.all`, `item.json.error`, `item.json`, `item.json.error?.message`, `item.json.error?.status`, `item.json.details?.description`. Constrói ou declara `json`, `source`, `status`, `post_count`, `errors`, `message`, `description` | `Unify Mastodon Posts` |
| `Status - social.espeweb.net` | Lê `input.all`, `item.json.error`, `item.json`, `item.json.error?.message`, `item.json.error?.status`, `item.json.details?.description`. Constrói ou declara `json`, `source`, `status`, `post_count`, `errors`, `message`, `description` | `Unify Mastodon Posts` |
| `Consolidar resultados` | Lê `input.all`, `item.json`. Constrói ou declara `json`, `status`, `total_posts`, `successful_sources`, `failed_sources`, `source`, `errors` | `If` |
| `Respond - No Posts` | HTTP `$('Consolidar resultados').first().json.status === 'error' ? 502 : 200` → `{ success: $('Consolidar resultados').first().json.status !== 'error', status: $('Consolidar resultados').first().json.status, message: $('Consolidar resultados').first().json.status === 'error' ? 'Falha na coleta: nenhuma das fontes retornou dados.' : 'Coleta concluída, mas nenhuma das fontes retornou novos posts. O arquivo existente não foi alterado.', total_posts: 0, successful_sources: $('Consolidar resultados').first().json.successful_sources, failed_sources: $('Consolidar resultados').first().json.failed_sources }` | Fim |
| `Prepare Search Parameter` | `tag` (string) ← `$json.body?.tag \|\| 'langsmith'`. Preserva outros campos | `Search hashtag - mastodon.social`, `Search hashtag - social.espeweb.net` |
| `Standard Mastodon Posts` | Constrói ou declara `source`, `author`, `text`, `tags`, `media_urls` | `Status - social.espeweb.net` |
| `Search hashtag - mastodon.social` | `'https://mastodon.social/api/v1/timelines/tag/' + $('Prepare Search Parameter').first().json.tag`. Query: `limit` → `40`. Emite resposta da API | `Standard Mastodon - Social Posts` |
| `Search hashtag - social.espeweb.net` | `'https://social.espeweb.net/api/v1/timelines/tag/' + $('Prepare Search Parameter').first().json.tag`. Query: `limit` → `40`. Emite resposta da API | `Standard Mastodon Posts` |

## wf07_coleta-hackernews

[wf07_coleta-hackernews.json](../n8n/workflows/wf07_coleta-hackernews.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `When clicking ‘Execute workflow’` | Disparo manual, sem campos de requisição | `Set Test Parameters` |
| `Convert to File` | Itens JSON → `binary.data` com nome `(() => { const input = $('If').first().json; const value = input.body?.query ?? input.query?.query ?? input.query; const theme = typeof value === 'string' ? value.trim() : ''; return 'hackernews_' + theme.replace(/[^a-zA-Z0-9_-]+/g, '') + '.json'; })()` | `Upload a file` |
| `Upload a file` | `binary.data` → objeto OCI `'raw/' + $binary.data.fileName` | `Valid Hacker News Research return` · Erro → `OCI Upload Error Response` |
| `Webhook` | `POST /webhook/wf07-hacker-news-search` → `headers`, `params`, `query`, `body` (Header Auth) | `If` |
| `If` | `(() => { const value = $json.body?.query ?? $json.query?.query ?? $json.query; return typeof value === 'string' ? value.trim() : ''; })()` notEmpty | Verdadeiro → `Search Hacker News` · Falso → `Invalid Query return` |
| `Search Hacker News` | `https://hn.algolia.com/api/v1/search`. Query: `query` → `(() => { const value = $json.body?.query ?? $json.query?.query ?? $json.query; return typeof value === 'string' ? value.trim() : ''; })()`, `tags` → `$json.body?.type ?? $json.query?.type ?? $json.type ?? 'story'`, `numericFilters` → `'created_at_i>=' + Math.floor( Number($json.body?.fromdate ?? $json.query?.fromdate ?? $json.fromdate) \|\| (Date.now() / 1000 - 30 * 24 * 60 * 60) ) + ( ($json.body?.type ?? $json.query?.type ?? $json.type ?? 'story') === 'story' ? ',points>=' + Math.max( 0, Number($json.body?.minPoints ?? $json.query?.minPoints ?? $json.minPoints) \|\| 0 ) : '' )`. Emite resposta da API | `Split Out Hits` · Erro → `Algolia Error Response` |
| `Invalid Query return` | HTTP `400` → `{ "error": "Parâmetro obrigatório ausente", "message": "Informe o parâmetro query com o tema que deseja pesquisar." }` | Fim |
| `Valid Hacker News Research return` | HTTP `200` → `{ success: true, message: 'Coleta concluída. Os posts do Hacker News foram armazenados no bucket OCI communitylab-assets.', }` | Fim |
| `Algolia Error Response` | HTTP `502` → `{ "error": "Falha na consulta externa", "message": "Não foi possível consultar o Hacker News. Tente novamente mais tarde." }` | Fim |
| `OCI Upload Error Response` | HTTP `502` → `{ "error": "Falha na persistência dos dados", "message": "A pesquisa foi processada, mas não foi possível armazenar os resultados. Tente novamente mais tarde." }` | Fim |
| `Set Test Parameters` | `query` (string) ← `$('Webhook').isExecuted ? ($json.body?.query ?? '') : 'langsmith'`, `type` (string) ← `story`, `limit` (number) ← `$('Webhook').isExecuted ? Number($json.body?.limit ?? 1) : 1`, `fromdate` (number) ← `Math.floor(Date.now() / 1000 - 30 * 24 * 60 * 60)`, `minPoints` (number) ← `10`, `maxCommentsPerStory` (number) ← `50` | `If` |
| `Consult Publication` | `=https://hacker-news.firebaseio.com/v0/item/{{ $json.objectID }}.json`. Emite resposta da API | `Prepare comments`, `Prepare publication` |
| `Split Out Hits` | `hits` → um item por elemento | `Filter` |
| `Prepare comments` | `pub_story_id` (number) ← `$json.id`, `pub_story_title` (string) ← `$json.title ?? ''`, `pub_depth` (number) ← `3`, `comment_id` (array) ← `(() => { const input = $('If').first().json; const value = Number( input.body?.maxCommentsPerStory ?? input.query?.maxCommentsPerStory ?? input.maxCommentsPerStory ?? 50 ); const limit = Number.isFinite(value) ? Math.min(50, Math.max(1, Math.floor(value))) : 50; return Array.isArray($json.kids) ? $json.kids.slice(0, limit) : []; })()` | `Split Out comments` |
| `Split Out comments` | `comment_id` → um item por elemento | `HTTP Request Comments` |
| `Add context` | `comment_id` (number) ← `$json.id`, `comment_author` (string) ← `$json.by`, `comment_kids` (array) ← `$json.kids`, `comment_text` (string) ← `$json.text`, `comment_time` (number) ← `$json.time`, `comment_type` (string) ← `$json.type`, `comment_parent` (number) ← `$json.parent` | `Merge` |
| `Prepare publication` | `pub_story_id` (number) ← `$json.id`, `pub_story_title` (string) ← `$json.title ?? ''`, `pub_depth` (number) ← `1`, `comment_id` (array) ← `$json.kids ?? []`, `pub_maxComments` (number) ← `Array.isArray($json.kids) ? $json.kids.length : 0`, `pub_score` (number) ← `$json.score`, `pub_time` (number) ← `$json.time`, `pub_url` (string) ← `$json.url`, `pub_author` (string) ← `$json.by`, `pub_text` (string) ← `$json.text` | `Merge` |
| `Merge` | Combina itens com `combine`, `{'values': [{'field1': 'pub_story_id', 'field2': 'comment_parent'}]}`, `enrichInput1` | `Convert to File` |
| `HTTP Request Comments` | `=https://hacker-news.firebaseio.com/v0/item/{{ $json.comment_id }}.json`. Emite resposta da API | `Add context` |
| `Filter` | `/^[1-9]\d*$/.test(String($json.objectID ?? ''))` true | `Has Eligible Publication` |
| `Has Eligible Publication` | `$json.objectID !== undefined && $json.objectID !== null` true | Verdadeiro → `Limit` · Falso → `Respond to Webhook` |
| `Respond to Webhook` | HTTP `200` → `{ "success": true, "message": "Nenhuma publicação elegível encontrada. Nenhum arquivo foi armazenado." }` | Fim |
| `Limit` | Máximo de `(() => { const input = $('If').first().json; const value = Number( input.body?.limit ?? input.query?.limit ?? input.limit ?? 2 ); return Number.isFinite(value) ? Math.min(20, Math.max(1, Math.floor(value))) : 2; })()` itens | `Consult Publication` |

## wf08_merge-stackexchange-data

[wf08_merge-stackexchange-data.json](../n8n/workflows/wf08_merge-stackexchange-data.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `When clicking ‘Execute workflow’` | Disparo manual, sem campos de requisição | `Get Tag` |
| `Get OCI Bucket files` | Lista `collected/` → `Key` e metadados | `Select sample_stackoverflow json files` |
| `Download a file` | `$json.Key` → `binary.data` | `Extract from File` |
| `Extract from File` | `binary.data` → JSON em `$binary.data.fileName.split('_')[1].split('-')[1]` | `Code in JavaScript` |
| `Select sample_stackoverflow json files` | `$json.Key ?? ''` endsWith `'_' + $('Loop Over Items').first(1, $runIndex).json.tagged + $('Loop Over Items').first(1, $runIndex).json.file_type` **AND** `$json.Key ?? ''` contains `'sample_' + $('Loop Over Items').first(1, $runIndex).json.source + '-'` | `Arquivo encontrado?` |
| `Code in JavaScript` | Lê `input.all`, `item.json`, `data.questions`, `data.licenses`, `data.answers`. Constrói ou declara `source_id`, `question`, `license`, `answers`, `json` | `Merge possui registros?` |
| `Convert to File` | Itens JSON → `binary.data` com nome `(() => { const indice = $node["Edit Fields"].runIndex; const parametros = $('Edit Fields').first(0, indice).json; return parametros.source + '_' + parametros.tagged + '.json'; })()` | `Upload a file` |
| `Define Search Parameters` | `file_type` (string) ← `.json`, `source` (string) ← `stackoverflow`, `tagged` (string) ← `$prevNode.name === 'Get Tag' ? $json.tag : ($json.body?.tagged ?? 'langsmith')` | `Loop Over Items` |
| `Webhook` | `GET /webhook/wf08_merge-stackexchange-data` → `headers`, `params`, `query`, `body` (Header Auth) | `Define Search Parameters` |
| `Respond to Webhook` | HTTP `200` → `{ "status": "success", "message": "Processamento concluído. Tags sem arquivos correspondentes ou sem registros foram ignoradas; os arquivos gerados foram enviados ao bucket OCI." }` | Fim |
| `Upload a file` | `binary.data` → objeto OCI `'raw/' + $binary.data.fileName` | `Loop Over Items` |
| `Get Tag` | Lê `social_topic` em ordem de `id` e usa `tag` nas iterações | `Define Search Parameters` |
| `Loop Over Items` | Itera sobre os itens em lotes de `1` | Concluído → `Respond to Webhook` · Iteração → `Edit Fields` |
| `Arquivo encontrado?` | `$json.Key ?? ''` notEmpty | Verdadeiro → `Download a file` · Falso → `Loop Over Items` |
| `Merge possui registros?` | `String($json.source_id ?? '').trim()` notEmpty | Verdadeiro → `Convert to File` · Falso → `Loop Over Items` |
| `Edit Fields` | `source` (string) ← `$('Define Search Parameters').item.json.source`, `tagged` (string) ← `$('Define Search Parameters').item.json.tagged`. Preserva outros campos | `Get OCI Bucket files` |
| `Sticky Note` | Nota de documentação no editor | Fim |

## wf09_triagem-llm-router_mastodon

[wf09_triagem-llm-router_mastodon.json](../n8n/workflows/wf09_triagem-llm-router_mastodon.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `When clicking ‘Execute workflow’` | Disparo manual, sem campos de requisição | `Define Search Parameters` |
| `Get OCI Bucket files` | Lista `raw/` → `Key` e metadados | `Select sample_ json files` |
| `Select sample_ json files` | `$json.Key.toLowerCase().replace(/\s+/g, '')` equals `( 'raw/' + $('Define Search Parameters').first().json.source + '_' + $('Define Search Parameters').first().json.tag + $('Define Search Parameters').first().json.file_type ).toLowerCase().replace(/\s+/g, '')` | `Download a file` |
| `Download a file` | `$json.Key` → `binary.data` | `Extract from File` |
| `Extract from File` | `binary.data` → JSON em `data` | `Split Out` |
| `Split Out` | `data[0].posts` → um item por elemento | `Sanitize HTML Text`, `Merge` |
| `Sanitize HTML Text` | `text` → `clean_text` | `Merge` |
| `Merge` | Combina itens com `combine`, `combineByPosition` | `Map Mastodon Fields` |
| `Map Mastodon Fields` | `post_id` (string) ← `$json.id`, `source` (string) ← `$json.source`, `author` (string) ← `$json.author`, `created_at` (string) ← `$json.created_at`, `language` (string) ← `$json.language`, `url` (string) ← `$json.url`, `clean_text` (string) ← `$json.clean_text.replace(/https?:\/\/\S+/g, '').trim()`, `tags` (array) ← `$json.tags`, `source_file` (string) ← `$('Download a file').item.json.Key`, `sensitive` (boolean) ← `$json.sensitive`, `replies_count` (number) ← `$json.replies_count`, `reblogs_count` (number) ← `$json.reblogs_count`, `edited_at` (string) ← `$json.edited_at`, `account.id` (string) ← `$json.account.id`, `account.followers_count` (number) ← `$json.account.followers_count`, `account.following_count` (number) ← `$json.account.following_count`, `account.username` (string) ← `$json.account.username`, `account.bot` (boolean) ← `$json.account.bot`, `account.statuses_count` (number) ← `$json.account.statuses_count`, `account.last_status_at` (string) ← `$json.account.last_status_at`, `account.created_at` (string) ← `$json.account.created_at`, `account.last_status_at` (string) ← `$json.account.last_status_at` | `Limit`, `Merge Infos` |
| `Sentiment Analysis` | `JSON.stringify($json)` → categoria de sentimento | `Edit Excited` · Erro → `Edit Happy` · Erro → `Edit Neutral` · Erro → `Edit Disappointed` · Erro → `Edit Angry` · Erro → `Prepare Error` |
| `Merge Evaluation` | Combina itens com `5` | `Merge Infos` |
| `Convert to File` | Itens JSON → `binary.data` com nome `"result_" + $('Define Search Parameters').item.json.source + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + ".json"` | `Upload a file` |
| `Limit` | Máximo de `$('Define Search Parameters').first().json.limit` itens | `Sentiment Analysis` |
| `Define Search Parameters` | `file_type` (string) ← `'.json'`, `source` (string) ← `'mastodon'`, `tag` (string) ← `$('Webhook').isExecuted ? ($json.body?.tag ?? '') : 'artificial intelligence'`, `limit` (number) ← `$('Webhook').isExecuted ? Number($json.body?.limit ?? 50) : 50`, `tag_key` (string) ← `String( $('Webhook').isExecuted ? ($json.body?.tag ?? '') : 'artificial intelligence' ).trim().toLowerCase().replace(/\s+/g, '')` | `Get OCI Bucket files` |
| `Edit Excited` | `post_id` (string) ← `$json.post_id`, `source` (string) ← `$json.source`, `sentiment` (string) ← `$json.sentimentAnalysis.category`, `strength` (number) ← `$json.sentimentAnalysis.strength`, `confidence` (number) ← `$json.sentimentAnalysis.confidence` | `Merge Evaluation` |
| `Edit Happy` | `post_id` (string) ← `$json.post_id`, `source` (string) ← `$json.source`, `sentiment` (string) ← `$json.sentimentAnalysis.category`, `strength` (number) ← `$json.sentimentAnalysis.strength`, `confidence` (number) ← `$json.sentimentAnalysis.confidence` | `Merge Evaluation` |
| `Edit Neutral` | `post_id` (string) ← `$json.post_id`, `source` (string) ← `$json.source`, `sentiment` (string) ← `$json.sentimentAnalysis.category`, `strength` (number) ← `$json.sentimentAnalysis.strength`, `confidence` (number) ← `$json.sentimentAnalysis.confidence` | `Merge Evaluation` |
| `Edit Disappointed` | `post_id` (string) ← `$json.post_id`, `source` (string) ← `$json.source`, `sentiment` (string) ← `$json.sentimentAnalysis.category`, `strength` (number) ← `$json.sentimentAnalysis.strength`, `confidence` (number) ← `$json.sentimentAnalysis.confidence` | `Merge Evaluation` |
| `Edit Angry` | `post_id` (string) ← `$json.post_id`, `source` (string) ← `$json.source`, `sentiment` (string) ← `$json.sentimentAnalysis.category`, `strength` (number) ← `$json.sentimentAnalysis.strength`, `confidence` (number) ← `$json.sentimentAnalysis.confidence` | `Merge Evaluation` |
| `Webhook` | `POST /webhook/wf09_triagem-llm-router-mastodon` → `headers`, `params`, `query`, `body` (Header Auth) | `Define Search Parameters` |
| `Respond to Webhook` | HTTP `200` → `$json` | Fim |
| `Upload a file` | `binary.data` → objeto OCI `'processed/' + $binary.data.fileName` | `Merge Switch` · Erro → `Prepare Storage Error` |
| `NVIDIA Nemotron Chat Model` | Modelo conectado ao nó de IA | ai_languageModel `Sentiment Analysis` |
| `AI Agent` | Usa o texto configurado no prompt → `output` | `Edit Fields` · Erro → `Prepare Error` |
| `Merge Infos` | Combina itens com `combine`, `post_id , source` | `AI Agent` |
| `Structured Output Parser` | Campos do esquema: `post_id`, `source`, `content_type`, `topics`, `relevance_score`, `summary`, `suggested_route`, `needs_human_review`, `assessment_note` | ai_outputParser `AI Agent` |
| `NVIDIA Nemotron Chat Model1` | Modelo conectado ao nó de IA | ai_languageModel `AI Agent` |
| `Edit Fields` | `post_id` (string) ← `$json.output.post_id`, `source` (string) ← `$json.output.source`, `clean_text` (string) ← `$('Merge Infos').item.json.clean_text`, `author` (string) ← `$('Merge Infos').item.json.author`, `url` (string) ← `$('Merge Infos').item.json.url`, `source_file` (string) ← `$('Merge Infos').item.json.source_file`, `sentiment` (string) ← `$('Merge Infos').item.json.sentiment`, `strength` (number) ← `$('Merge Infos').item.json.strength`, `confidence` (number) ← `$('Merge Infos').item.json.confidence`, `editorial` (object) ← `{ content_type: $json.output.content_type, topics: $json.output.topics, relevance_score: $json.output.relevance_score, summary: $json.output.summary, suggested_route: $json.output.suggested_route, needs_human_review: $json.output.needs_human_review, assessment_note: $json.output.assessment_note }`, `created_at` (string) ← `$('Split Out').item.json.created_at`, `language` (string) ← `$('Merge Infos').item.json.language`, `tags` (array) ← `$('Merge Infos').item.json.tags`, `sensitive` (boolean) ← `$('Merge Infos').item.json.sensitive`, `replies_count` (number) ← `$('Merge Infos').item.json.replies_count`, `reblogs_count` (number) ← `$('Merge Infos').item.json.reblogs_count`, `account.id` (string) ← `$('Merge Infos').item.json.account.id`, `account.followers_count` (number) ← `$('Merge Infos').item.json.account.followers_count`, `account.following_count` (number) ← `$('Merge Infos').item.json.account.following_count`, `account.bot` (boolean) ← `$('Merge Infos').item.json.account.bot`, `account.statuses_count` (number) ← `$('Merge Infos').item.json.account.statuses_count`, `account.last_status_at` (string) ← `$('Merge Infos').item.json.account.last_status_at`, `account.created_at` (string) ← `$('Merge Infos').item.json.account.created_at` | `Convert to File`, `If Human Review` · Erro → `Prepare Error` |
| `If Human Review` | `$json.editorial.needs_human_review` true `False` | Verdadeiro → `Mark Human Review` · Falso → `Editorial Route` |
| `Mark Human Review` | `routing.destination` (string) ← `human_review`, `routing.status` (string) ← `pending_review`. Preserva outros campos | `Convert to File true` |
| `Editorial Route` | `$json.editorial.suggested_route` equals `success_case` / `$json.editorial.suggested_route` equals `faq` / `$json.editorial.suggested_route` equals `newsletter_only` / `$json.editorial.suggested_route` equals `moderation` / `$json.editorial.suggested_route` equals `discard` | 1 → `Success Case` · 2 → `FAQ` · 3 → `Newsletter` · 4 → `Moderation` · 5 → `Discard` · Fallback → `Fallback` |
| `Success Case` | `routing.destination` (string) ← `success_case`, `routing.status` (string) ← `pending_generation`. Preserva outros campos | `Convert to File false` |
| `FAQ` | `routing.destination` (string) ← `faq`, `routing.status` (string) ← `pending_generation`. Preserva outros campos | `Convert to File false1` |
| `Newsletter` | `routing.destination` (string) ← `newsletter`, `routing.status` (string) ← `pending_generation`. Preserva outros campos | `Convert to File false2` |
| `Moderation` | `routing.destination` (string) ← `human_review`, `routing.status` (string) ← `pending_review`. Preserva outros campos | `Convert to File false3` |
| `Discard` | `routing.destination` (string) ← `discard`, `routing.status` (string) ← `discarded`. Preserva outros campos | `Convert to File false4` |
| `Fallback` | `routing.destination` (string) ← `human_review`, `routing.status` (string) ← `invalid_route`. Preserva outros campos | `Convert to File false5` |
| `Convert to File true` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file true` |
| `Upload a file true` | `binary.data` → objeto OCI `'processed/routing/human_review/' + $binary.data.fileName` | `Merge Switch` · Erro → `Prepare Storage Error` |
| `Convert to File false` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false` |
| `Upload a file false` | `binary.data` → objeto OCI `'processed/routing/success_case/' + $binary.data.fileName` | `Merge Switch` · Erro → `Prepare Storage Error` |
| `Convert to File false1` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false1` |
| `Convert to File false2` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false2` |
| `Convert to File false3` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false3` |
| `Convert to File false4` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false4` |
| `Convert to File false5` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false5` |
| `Upload a file false1` | `binary.data` → objeto OCI `'processed/routing/faq/' + $binary.data.fileName` | `Merge Switch` · Erro → `Prepare Storage Error` |
| `Upload a file false2` | `binary.data` → objeto OCI `'processed/routing/newsletter/' + $binary.data.fileName` | `Merge Switch` · Erro → `Prepare Storage Error` |
| `Upload a file false3` | `binary.data` → objeto OCI `'processed/routing/moderation/' + $binary.data.fileName` | `Merge Switch` · Erro → `Prepare Storage Error` |
| `Upload a file false4` | `binary.data` → objeto OCI `'processed/routing/discard/' + $binary.data.fileName` | `Merge Switch` · Erro → `Prepare Storage Error` |
| `Upload a file false5` | `binary.data` → objeto OCI `'processed/routing/invalid_route/' + $binary.data.fileName` | `Merge Switch` · Erro → `Prepare Storage Error` |
| `Merge Switch` | Combina itens com `8` | `Prepare Success Response` |
| `Prepare Error` | `success` (boolean) ← `False`, `status` (string) ← `error`, `error_code` (string) ← `SCREENING_FAILED`, `message` (string) ← `Não foi possível concluir a classificação das publicações do Mastodon.`, `source` (string) ← `mastodon`, `execution_id` (string) ← `$execution.id` | `Screening Error Message` |
| `Screening Error Message` | HTTP `502` → `$json` | Fim |
| `Prepare Storage Error` | `success` (boolean) ← `False`, `status` (string) ← `error`, `error_code` (string) ← `STORAGE_UPLOAD_FAILED`, `message` (string) ← `Não foi possível concluir a gravação dos resultados do Mastodon na OCI. Pode haver arquivos parcialmente gravados.`, `source` (string) ← `mastodon`, `execution_id` (string) ← `$execution.id` | `Storage Error Message` |
| `Storage Error Message` | HTTP `502` → `$json` | Fim |
| `Prepare Success Response` | Lê `item.json`. Constrói ou declara `json`, `success`, `status`, `source`, `tag`, `execution_id`, `count`, `items`, `storage`, `bucket`, `object_path` | `Respond to Webhook` |

## wf10_triagem-llm-router_stackexchange

[wf10_triagem-llm-router_stackexchange.json](../n8n/workflows/wf10_triagem-llm-router_stackexchange.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `When clicking ‘Execute workflow’` | Disparo manual, sem campos de requisição | `Define Search Parameters` |
| `Get OCI Bucket files` | Lista `raw/` → `Key` e metadados | `Select sample_ json files` |
| `Select sample_ json files` | `$json.Key` equals `(() => { const { source, tag, file_type } = $('Define Search Parameters').first().json; const normalizedTag = tag.trim().replace(/\s+/g, ''); return raw/${source}_${normalizedTag}${file_type}; })()` | `Download a file` |
| `Download a file` | `$json.Key` → `binary.data` | `Extract from File` |
| `Extract from File` | `binary.data` → JSON em `data` | `Split Out` |
| `Split Out` | `data` → um item por elemento | `Filter` |
| `Convert to File` | Itens JSON → `binary.data` com nome `"result_" + $('Define Search Parameters').item.json.source + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + ".json"` | `Upload a file` |
| `Limit` | Máximo de `$('Define Search Parameters').item.json.limit` itens | `Filter1` |
| `Define Search Parameters` | `file_type` (string) ← `'.json'`, `source` (string) ← `'stackoverflow'`, `tag` (string) ← `$('Webhook').isExecuted ? ($json.body?.tag ?? '') : 'langsmith'`, `limit` (number) ← `$('Webhook').isExecuted ? Number($json.body?.limit ?? 1) : 1` | `Get OCI Bucket files` |
| `Webhook` | `POST /webhook/wf10_triagem-llm-router_stackexchange` → `headers`, `params`, `query`, `body` (Header Auth) | `Define Search Parameters` |
| `Respond to Webhook` | HTTP `200` → `$json` | Fim |
| `Upload a file` | `binary.data` → objeto OCI `'processed/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `NVIDIA Nemotron Chat Model` | Modelo conectado ao nó de IA | ai_languageModel `AI Agent` |
| `Filter` | `$json.body_question` exists **AND** `$json.body_question` notEmpty | `Map StackOverflow Fields` |
| `Map StackOverflow Fields` | `source_id` (string) ← `$json.source_id`, `source` (string) ← `=stackoverflow`, `question_author` (string) ← `$json.owner_question`, `question_title` (string) ← `$json.title_question`, `question_date_created_at` (string) ← `$json.creation_date_question`, `question_url` (string) ← `$json.link_question`, `question_body` (string) ← `$json.body_question`, `tags` (array) ← `$json.tags`, `source_file` (string) ← `$('Download a file').item.json.Key`, `question_score` (number) ← `$json.score_question`, `question_last_activity_date` (number) ← `$json.last_activity_date_question`, `question_answer_count` (number) ← `$json.answer_count_question`, `question_comment_count` (number) ← `$json.comment_count_question`, `answers` (array) ← `$json.answers` | `Limit` |
| `AI Agent` | Usa o texto configurado no prompt → `output` | `Merge Classification` · Erro → `Prepare Error` |
| `Structured Output Parser` | Campos do esquema: `source_id`, `source`, `answers` | ai_outputParser `AI Agent` |
| `Merge Classification` | Lê `input.all`, `classification.answer_id`, `classification.original_language`, `classification.sentiment`, `classification.strength`, `classification.confidence`, `classification.content_type`, `classification.topics`, `classification.relevance_score`, `classification.summary`, `classification.suggested_route`, `classification.needs_human_review`, `classification.assessment_note`, `item.json.output`, `result.source_id`, `result.answers`, `result.answers.map`, `result.source`. Constrói ou declara `json`, `pairedItem`, `item` | `Convert to File`, `If Human Review` · Erro → `Prepare Error` |
| `Mark Human Review` | `routing.destination` (string) ← `human_review`, `routing.status` (string) ← `pending_review`. Preserva outros campos | `Convert to File true` |
| `Editorial Route` | `$json.suggested_route` equals `success_case` / `$json.suggested_route` equals `faq` / `$json.suggested_route` equals `newsletter_only` / `$json.suggested_route` equals `moderation` / `$json.suggested_route` equals `discard` | 1 → `Success Case` · 2 → `Faq` · 3 → `Newsletter` · 4 → `Moderation` · 5 → `Discard` · Fallback → `Fallback` |
| `Success Case` | `routing.destination` (string) ← `success_case`, `routing.status` (string) ← `pending_generation`. Preserva outros campos | `Convert to File false5` |
| `Faq` | `routing.destination` (string) ← `faq`, `routing.status` (string) ← `pending_generation`. Preserva outros campos | `Convert to File false` |
| `Newsletter` | `routing.destination` (string) ← `newsletter`, `routing.status` (string) ← `pending_generation`. Preserva outros campos | `Convert to File false1` |
| `Moderation` | `routing.destination` (string) ← `human_review`, `routing.status` (string) ← `pending_review`. Preserva outros campos | `Convert to File false2` |
| `Discard` | `routing.destination` (string) ← `discard`, `routing.status` (string) ← `discarded`. Preserva outros campos | `Convert to File false3` |
| `Fallback` | `routing.destination` (string) ← `human_review`, `routing.status` (string) ← `invalid_route`. Preserva outros campos | `Convert to File false4` |
| `Upload a file false` | `binary.data` → objeto OCI `'processed/routing/faq/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Upload a file false1` | `binary.data` → objeto OCI `'processed/routing/newsletter/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Convert to File false` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false` |
| `Convert to File false1` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false1` |
| `Convert to File false2` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false2` |
| `Convert to File false3` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false3` |
| `Convert to File false4` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false4` |
| `Upload a file false2` | `binary.data` → objeto OCI `'processed/routing/moderation/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Upload a file false3` | `binary.data` → objeto OCI `'processed/routing/discard/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Upload a file false4` | `binary.data` → objeto OCI `'processed/routing/fallback/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Merge` | Combina itens com `8` | `Prepare Success Response` |
| `NVIDIA Chat Model` | Modelo conectado ao nó de IA | ai_languageModel `AI Agent` |
| `Convert to File false5` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false5` |
| `Convert to File true` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false6` |
| `Upload a file false5` | `binary.data` → objeto OCI `'processed/routing/success_case/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Upload a file false6` | `binary.data` → objeto OCI `'processed/routing/human_review/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `If Human Review` | `$json.needs_human_review` true `False` | Verdadeiro → `Mark Human Review` · Falso → `Editorial Route` |
| `Filter1` | Desativado. `$json.source_id` equals `79965487` | `AI Agent` |
| `Prepare Error` | `status` (string) ← `error`, `error` (string) ← `triage_failed`, `message` (string) ← `Não foi possível concluir ou validar a classificação do lote.`, `execution_id` (string) ← `$execution.id` | `Screening Error Message` |
| `Screening Error Message` | HTTP `502` → `$json` | Fim |
| `Prepare Storage Error` | `success` (boolean) ← `False`, `status` (string) ← `error`, `error_code` (string) ← `STORAGE_UPLOAD_FAILED`, `message` (string) ← `Não foi possível concluir a gravação dos resultados do Stack Overflow na OCI. Pode haver arquivos parcialmente gravados.`, `source` (string) ← `stackoverflow`, `execution_id` (string) ← `$execution.id` | `Storage Error Message` |
| `Storage Error Message` | HTTP `502` → `$json` | Fim |
| `Prepare Success Response` | Lê `item.json`. Constrói ou declara `json`, `success`, `status`, `source`, `tag`, `execution_id`, `count`, `items`, `storage`, `bucket`, `object_path` | `Respond to Webhook` |

## wf11_triagem-llm-router_hackernews

[wf11_triagem-llm-router_hackernews.json](../n8n/workflows/wf11_triagem-llm-router_hackernews.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `When clicking ‘Execute workflow’` | Disparo manual, sem campos de requisição | `Define Search Parameters` |
| `Get OCI Bucket files` | Lista `raw/` → `Key` e metadados | `Select sample_ json files` |
| `Select sample_ json files` | `$json.Key` equals `(() => { const { source, tag, file_type } = $('Define Search Parameters').first().json; const tagKey = tag.toLowerCase().replace(/\s+/g, ''); return raw/${source}_${tagKey}${file_type}; })()` | `Download a file` |
| `Download a file` | `$json.Key` → `binary.data` | `Extract from File` |
| `Extract from File` | `binary.data` → JSON em `data` | `Split Out` |
| `Split Out` | `data` → um item por elemento | `Filter Comments` |
| `Convert to File` | Itens JSON → `binary.data` com nome `'result_hackernews_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '.json'` | `Upload a file` |
| `Limit` | Máximo de `$('Define Search Parameters').first().json.limit` itens | `AI Agent` |
| `Define Search Parameters` | `file_type` (string) ← `'.json'`, `source` (string) ← `'hackernews'`, `tag` (string) ← `$('Webhook').isExecuted ? (typeof $json.body?.tag === 'string' ? $json.body.tag.trim() : '') : 'langsmith'`, `limit` (number) ← `$('Webhook').isExecuted ? (typeof $json.body?.limit === 'number' ? $json.body.limit : 0) : 5` | `Validate Search Parameters` |
| `Webhook` | `POST /webhook/wf11_triagem-llm-router_hackernews` → `headers`, `params`, `query`, `body` (Header Auth) | `Define Search Parameters` |
| `Respond to Webhook` | HTTP `200` → `$json` | Fim |
| `Upload a file` | `binary.data` → objeto OCI `'processed/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `NVIDIA Nemotron Chat Model` | Modelo conectado ao nó de IA | ai_languageModel `AI Agent` |
| `Map HackerNews Fields` | `source_file` (string) ← `$('Download a file').item.json.Key`, `post.source` (string) ← `$('Define Search Parameters').item.json.source`, `post.id` (string) ← `$json.pub_story_id`, `post.title` (string) ← `$json.pub_story_title`, `post.author` (string) ← `$json.pub_author`, `post.created_at` (string) ← `$json.pub_time`, `post.author` (string) ← `$json.pub_author`, `post.url` (string) ← `$json.pub_url`, `post.text` (string) ← `$json.pub_text`, `post.maxComments` (number) ← `$json.pub_maxComments`, `post.comments_count` (number) ← `$json.pub_maxComments`, `post.score` (number) ← `$json.pub_score`, `comment.time` (number) ← `$json.comment_time`, `comment.type` (string) ← `$json.comment_type`, `comment.author` (string) ← `$json.comment_author`, `comment.id` (string) ← `$json.comment_id`, `comment.n_subcomments` (string) ← `$if($json.comment_kids && $json.comment_kids.length > 0, $json.comment_kids.length, 0 )`, `comment.text` (string) ← `$json.comment_text` | `Limit` |
| `AI Agent` | Usa o texto configurado no prompt → `output` | `Merge Classification` · Erro → `Prepare Error` |
| `Filter Comments` | `$json.comment_text` exists **AND** `$json.comment_text` notEmpty | `Map HackerNews Fields` |
| `OpenAI Chat Model` | Modelo conectado ao nó de IA | ai_languageModel `AI Agent` |
| `Structured Output Parser` | Campos do esquema: `post_id`, `source`, `comments` | ai_outputParser `AI Agent` |
| `Merge Classification` | Lê `input.all`, `classification.comment_id`, `classification.original_language`, `classification.sentiment`, `classification.strength`, `classification.confidence`, `classification.content_type`, `classification.topics`, `classification.relevance_score`, `classification.summary`, `classification.suggested_route`, `classification.needs_human_review`, `classification.assessment_note`, `post.id`, `post.source`, `item.json.output`, `result.post_id`, `result.source`, `result.comments`, `result.comments.length`. Constrói ou declara `json`, `pairedItem`, `item` | `Convert to File`, `If` · Erro → `Prepare Error` |
| `If` | `$json.needs_human_review` true `False` | Verdadeiro → `Mark Human Review` · Falso → `Editorial Route` |
| `Mark Human Review` | `routing.destination` (string) ← `human_review`, `routing.status` (string) ← `pending_review`. Preserva outros campos | `Convert to File true` |
| `Success Case` | `routing.destination` (string) ← `success_case`, `routing.status` (string) ← `pending_generation`. Preserva outros campos | `Convert to File false5` |
| `Faq` | `routing.destination` (string) ← `faq`, `routing.status` (string) ← `pending_generation`. Preserva outros campos | `Convert to File false` |
| `Newsletter` | `routing.destination` (string) ← `newsletter`, `routing.status` (string) ← `pending_generation`. Preserva outros campos | `Convert to File false1` |
| `Moderation` | `routing.destination` (string) ← `human_review`, `routing.status` (string) ← `pending_review`. Preserva outros campos | `Convert to File false2` |
| `Discard` | `routing.destination` (string) ← `discard`, `routing.status` (string) ← `discarded`. Preserva outros campos | `Convert to File false3` |
| `Fallback` | `routing.destination` (string) ← `human_review`, `routing.status` (string) ← `invalid_route`. Preserva outros campos | `Convert to File false4` |
| `Editorial Route` | `$json.suggested_route` equals `success_case` / `$json.suggested_route` equals `faq` / `$json.suggested_route` equals `newsletter_only` / `$json.suggested_route` equals `moderation` / `$json.suggested_route` equals `discard` | 1 → `Success Case` · 2 → `Faq` · 3 → `Newsletter` · 4 → `Moderation` · 5 → `Discard` · Fallback → `Fallback` |
| `Upload a file false` | `binary.data` → objeto OCI `'processed/routing/faq/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Upload a file false1` | `binary.data` → objeto OCI `'processed/routing/newsletter/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Convert to File false` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false` |
| `Convert to File false1` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false1` |
| `Convert to File false2` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false2` |
| `Convert to File false3` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false3` |
| `Convert to File false4` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false4` |
| `Upload a file false2` | `binary.data` → objeto OCI `'processed/routing/moderation/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Upload a file false3` | `binary.data` → objeto OCI `'processed/routing/discard/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Upload a file false4` | `binary.data` → objeto OCI `'processed/routing/fallback/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Merge` | Combina itens com `8` | `Prepare Success Response` |
| `Convert to File false5` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false5` |
| `Convert to File true` | Itens JSON → `binary.data` com nome `'result_' + $('Define Search Parameters').item.json.source + '_' + $json.routing.destination + '_' + $('Define Search Parameters').item.json.tag.replace(' ','') + '_' + $execution.id + '.json'` | `Upload a file false6` |
| `Upload a file false5` | `binary.data` → objeto OCI `'processed/routing/success_case/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Upload a file false6` | `binary.data` → objeto OCI `'processed/routing/human_review/' + $binary.data.fileName` | `Merge` · Erro → `Prepare Storage Error` |
| `Prepare Error` | `success` (boolean) ← `False`, `status` (string) ← `error`, `error_code` (string) ← `SCREENING_FAILED`, `message` (string) ← `Não foi possível concluir a classificação dos comentários do Hacker News.`, `source` (string) ← `hackernews`, `execution_id` (string) ← `$execution.id` | `Screening Error Message` |
| `Screening Error Message` | HTTP `502` → `$json` | Fim |
| `Prepare Storage Error` | `success` (boolean) ← `False`, `status` (string) ← `error`, `error_code` (string) ← `STORAGE_UPLOAD_FAILED`, `message` (string) ← `Não foi possível concluir a gravação dos resultados do Hacker News na OCI. Pode haver arquivos parcialmente gravados.`, `source` (string) ← `hackernews`, `execution_id` (string) ← `$execution.id` | `Storage Error Message` |
| `Storage Error Message` | HTTP `502` → `$json` | Fim |
| `Prepare Success Response` | Lê `item.json`. Constrói ou declara `json`, `success`, `status`, `source`, `tag`, `execution_id`, `count`, `items`, `storage`, `bucket`, `object_path` | `Respond to Webhook` |
| `Validate Search Parameters` | `$json.tag.length > 0 && Number.isSafeInteger($json.limit) && $json.limit > 0` true | Verdadeiro → `Get OCI Bucket files` · Falso → `Respond to Webhook1` |
| `Respond to Webhook1` | HTTP `400` → `firstIncomingItem` | Fim |

## wf12_consulta_resultados_processados

[wf12_consulta_resultados_processados.json](../n8n/workflows/wf12_consulta_resultados_processados.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `Webhook` | `GET /webhook/wf12-processed-results` → `headers`, `params`, `query`, `body` (Header Auth) | `Validate Request` |
| `Extract from File` | `binary.data` → JSON em `data` | `Prepare Return` · Erro → `Prepare Extraction Error` |
| `Prepare Return` | Lê `input.first`, `input.data`, `request.source`, `request.tag`, `request.object_key`, `input.data.length`. Constrói ou declara `json`, `success`, `statusCode`, `source`, `tag`, `object_key`, `error`, `code`, `message`, `count`, `items` | `Respond to Webhook` |
| `Respond to Webhook` | HTTP `$json.statusCode` → `$json` | Fim |
| `When clicking ‘Execute workflow’` | Disparo manual, sem campos de requisição | `Manual Test` |
| `Manual Test` | `query` (object) ← `={ "source": "stackoverflow", "tag": "artificialintelligence" }` | `Validate Request` |
| `Validate Request` | Lê `input.first`, `query.source`, `query.tag`, `query.tag.length`. Constrói ou declara `json`, `success`, `statusCode`, `error`, `code`, `object_key` | `Request Is Valid` |
| `Request Is Valid` | `$json.success` true | Verdadeiro → `Download a file` · Falso → `Respond Invalid Request` |
| `Download a file` | `$json.object_key` → `binary.data` | `Extract from File` · Erro → `Prepare Download Error` |
| `Respond Invalid Request` | HTTP `400` → `$json` | Fim |
| `Prepare Download Error` | Lê `input.first`, `input.error`, `input.error.trim`, `input.source`, `input.tag`, `input.object_key`. Constrói ou declara `json`, `success`, `statusCode`, `source`, `tag`, `object_key`, `error`, `code`, `message` | `Respond to Webhook` |
| `Prepare Extraction Error` | Lê `request.source`, `request.tag`, `request.object_key`. Constrói ou declara `json`, `success`, `statusCode`, `source`, `tag`, `object_key`, `error`, `code`, `message` | `Respond to Webhook` |

## wf13_interacao_analise_sentimento

[wf13_interacao_analise_sentimento.json](../n8n/workflows/wf13_interacao_analise_sentimento.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `AI Agent` | Usa `$json.chatInput` no prompt → `output` | `Prepare Chat Response` · Erro → `Prepare Agent Error` |
| `NVIDIA Nemotron Chat Model` | Modelo conectado ao nó de IA | ai_languageModel `AI Agent` |
| `OpenRouter Chat Model` | Modelo conectado ao nó de IA | ai_languageModel `AI Agent` |
| `Receive Dashboard Question` | `POST /webhook/wf13-sentimento-chat` → `headers`, `params`, `query`, `body` (Header Auth) | `Validate Dashboard Request` |
| `Validate Dashboard Request` | Lê `input.first`, `body.request_id`, `body.session_id`, `body.question`, `body.history`, `body.context`, `context.snapshot_id`, `context.loaded_at`, `context.filters`, `context.metrics`, `context.metrics.unique_interactions`, `context.evidence`, `context.evidence.length`, `context.limitations`, `context.limitations.some`, `body.request_id.slice`, `body.request_id.trim`, `body.session_id.trim`, `body.question.trim`. Constrói ou declara `json`, `valid`, `request_id`, `http_status`, `error_code`, `errors`, `session_id`, `question` | `Is Dashboard Request Valid` |
| `Is Dashboard Request Valid` | `$json.valid` true | Verdadeiro → `Prepare Agent Input` · Falso → `Respond Invalid Request` |
| `Prepare Agent Input` | Lê `input.first`, `request.question`, `request.history.map`, `request.context.snapshot_id`, `request.context.loaded_at`, `request.context.filters`, `request.context.metrics`, `request.context.evidence`, `request.context.limitations`, `request.request_id`, `request.session_id`. Constrói ou declara `question`, `history`, `role`, `content`, `context`, `snapshot_id`, `loaded_at`, `filters`, `metrics`, `evidence`, `limitations`, `json`, `request_id`, `session_id`, `chatInput` | `Resolve Theme Ranking` |
| `Prepare Chat Response` | Lê `input.first`, `result.output`, `result.output.trim`, `request.request_id`, `request.snapshot_id`. Constrói ou declara `json`, `http_status`, `body`, `request_id`, `status`, `error_code`, `message`, `snapshot_id` | `Respond Chat Response` |
| `Respond Chat Response` | HTTP `$json.http_status` → `$json.body` | Fim |
| `Respond Invalid Request` | HTTP `400` → `{ request_id: $json.request_id, status: "error", error_code: $json.error_code, message: "A pergunta ou o contexto enviado é inválido.", errors: $json.errors }` | Fim |
| `Prepare Agent Error` | Lê `request.request_id`, `request.snapshot_id`. Constrói ou declara `json`, `http_status`, `body`, `request_id`, `snapshot_id`, `status`, `error_code`, `message` | `Respond Chat Response` |
| `Resolve Theme Ranking` | Lê `chatInput` e as métricas por tema do contexto. Emite `deterministic` e, quando calcula o ranking de confiança ou relevância, `output` | `Is Theme Ranking` |
| `Is Theme Ranking` | `$json.deterministic` true `True` | Verdadeiro → `Prepare Chat Response` · Falso → `AI Agent` |

## Anexo de testes e subworkflow

- O subworkflow de classificação declara `active: true` e recebe chamadas de outro workflow. Nenhum workflow versionado referencia seu ID ou possui um nó que o invoque. WF09, WF10 e WF11 têm agentes próprios.
- WF00 implementa o protótipo `POST test-ingestion` com upload na OCI. A [especificação da OCI](specs/oci-object-storage-n8n.md) registra o uso da rota em teste. O export omite `active`.
- WF01 usa a mesma rota e apenas responde ao webhook. O export declara `active: false`.

O serviço de ingestão do aplicativo usa `/webhook/ingestion` por padrão. Não foi identificada referência operacional a `test-ingestion` no aplicativo. Chamadas externas e publicação dessas exportações dependem de confirmação no n8n.

### subwf_skill_router_classification

[subwf_skill_router_classification.json](../n8n/workflows/subwf_skill_router_classification.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `When Executed by Another Workflow` | Entradas do workflow pai: `skill_id (string)`, `context (object)` | `Resolve Router Skill` |
| `Resolve Router Skill` | Lê `context.source`, `context.content_type`. Constrói ou declara `content_classification`, `instructions`, `sentiment_analysis`, `relevance_scoring`, `Considere`, `routing_rules`, `edge_cases`, `json`, `skill_id`, `context`, `source`, `content_type` | Fim |

### WF00 - OCI Object Storage Ingestion

[wf00_oci-object-storage-ingestion.json](../n8n/workflows/wf00_oci-object-storage-ingestion.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `Webhook Receptor` | `POST /webhook/test-ingestion` → `headers`, `params`, `query`, `body` | `Processa Payload` |
| `Processa Payload` | Lê `input.all`, `item.json.body`, `item.json`. Constrói ou declara `json`, `status`, `message`, `received_at`, `payload_keys`, `payload` | `Convert to File` |
| `Resposta de Sucesso` | HTTP `200` → `{ success: true, message: $json.message, timestamp: $json.received_at, detected_fields: $json.payload_keys }` | Fim |
| `Upload a file` | `binary.data` → objeto OCI `tests/communitylab-ingestion-test.json` | `Resposta de Sucesso` |
| `Convert to File` | Itens JSON → `binary.data` com nome `data` | `Upload a file` |

### WF01 - Webhook Ingestion

[wf01_webhook-ingestion.json](../n8n/workflows/wf01_webhook-ingestion.json)

| Nó | Dados e regras | Conexões |
| --- | --- | --- |
| `Webhook Receptor` | `POST /webhook/test-ingestion` → `headers`, `params`, `query`, `body` | `Processa Payload` |
| `Processa Payload` | Lê `input.all`, `item.json.body`, `item.json`. Constrói ou declara `json`, `status`, `message`, `received_at`, `payload_keys` | `Resposta de Sucesso` |
| `Resposta de Sucesso` | HTTP `200` → `{ success: true, message: $json.message, timestamp: $json.received_at, detected_fields: $json.payload_keys }` | Fim |
