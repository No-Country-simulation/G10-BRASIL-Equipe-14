# Contrato de API — Stack Exchange

**Projeto:** CommunityLab — MVP  
**Base dos webhooks:** `https://bot.rsa.ia.br/webhook/`  
**Formato:** JSON UTF-8; WF05 entrega ZIP.  
**Referência:** análise estática dos workflows exportados; para o WF10, consulta adicional à versão publicada no n8n e às execuções existentes em 09/11/2026. Execução em produção não validada nesta revisão.

**Estado do WF10: implementado, publicado e validado em execução manual para o MVP (09/11/2026).** Rascunho e versão publicada estão sincronizados; a exportação local tem o mesmo identificador de versão (`0b760310-d4ee-4978-95da-361701b98a2a`). A execução 10216 processou dez perguntas e 16 respostas, com roteamento individual, revisão humana, uploads e conclusão. A execução 10212 também validou uma pergunta com 15 respostas e três destinos. O webhook de produção, o caminho de caso de sucesso e a qualidade editorial ainda precisam de validação específica. Os arquivos são agrupados por lote/ramo, embora os nomes usem o ID da primeira pergunta recebida.

## 1. Operações

| Workflow | Método e caminho relativo | Resultado |
| --- | --- | --- |
| [WF02](../../n8n/workflows/wf02_coleta-stack-exchange-questions-integrada.json) | `POST wf02-coleta-stack-exchange` | Coleta e sanitiza perguntas; grava JSON na OCI |
| [WF03](../../n8n/workflows/wf03_coleta-stack-exchange-licenses-integrada.json) | `POST wf03-coleta-stack-exchange-licenses` | Coleta licenças das perguntas; grava JSON na OCI |
| [WF04](../../n8n/workflows/wf04_coleta-stack-exchange-answer-integrada.json) | `POST wf04-coleta-stack-exchange-answers` | Busca perguntas e coleta suas respostas em lotes de até 100 IDs; grava JSON na OCI |
| [WF05](../../n8n/workflows/wf05_download-bucket-OCI.json) | `GET wf05-download-bucket-OCI` | Baixa os objetos listados no bucket e devolve um ZIP |
| [WF08](../../n8n/workflows/wf08_merge-stackexchange-data.json) | `GET wf08_merge-stackexchange-data` | Combina perguntas, licenças e respostas por `source_id`; grava em `raw/` |
| [WF10](../../n8n/workflows/wf10_triagem-llm-router_stackexchange.json) | `POST wf10_triagem-llm-router_stackexchange` | Avalia idioma, sentimento e atributos editoriais; roteia cada resposta e configura persistência em `processed/` e nas filas editoriais |

WF02, WF03, WF04, WF05, WF08 e a versão publicada do WF10 configuram `Header Auth`. Enviar `communitylab-api-key: <SUA_CHAVE_DE_API>`, conforme [credenciais n8n](./n8n-credentials.md).

As operações são independentes: executar WF02, WF03 e WF04 com os mesmos parâmetros, depois WF08 e WF10. WF05 serve para baixar os arquivos. Não há encadeamento automático entre esses workflows.

## 2. Entrada da coleta — WF02, WF03 e WF04

Enviar um objeto JSON no corpo do POST, com `Content-Type: application/json`. Campos omitidos ou nulos usam os padrões abaixo.

| Campo | Padrão | Validação implementada |
| --- | --- | --- |
| `tagged` | `artificial-intelligence` | String não vazia, até 200 caracteres; padrão `^[a-zA-Z0-9.+#_;-]+$` |
| `fromdate` | `1760929200` | Convertido com `Number`; inteiro seguro positivo, em segundos Unix, sem data futura |
| `pagesize` | `100` | Convertido com `Number`; inteiro entre 1 e 100 |
| `site` | `stackoverflow` | String não vazia, até 100 caracteres; padrão `^[a-z0-9.-]+$` |

```json
{
  "tagged": "artificial-intelligence",
  "fromdate": 1760929200,
  "pagesize": 100,
  "site": "stackoverflow"
}
```

A coleta ordena por votos decrescentes e pagina até `has_more === false`, e `pagesize` não limita o total coletado. A validação de `site` verifica formato, sem consultar se a comunidade existe. Para o MVP, utilizar `stackoverflow`.

WF05 não recebe filtro de download. WF08 e WF10 usam `source=stackoverflow` e extensão `.json` fixos nos nós de configuração; o corpo da requisição não altera esses valores.

## 3. Arquivos e dados

Todos os arquivos são armazenados no bucket `communitylab-assets`, acessado pelos nós S3.

| Etapa | Chave do objeto / estrutura |
| --- | --- |
| WF02 | `sample_{site}-questions_{tagged}.json`: perguntas com `source_id` string, título, corpo HTML, autor, link, tags e métricas com sufixo `_question` |
| WF03 | `sample_{site}-questions-licenses_{tagged}.json`: `source_id` e `content_license_question` (pode ser `null`) |
| WF04 | `sample_{site}-answers_{tagged_normalizada}.json`: `source_id` string, `answer_id` e campos dinâmicos como `body_answer_{account_id}`, autor, licença e métricas |
| WF08 | `raw/{nome_derivado}.json`: um registro por `source_id`, campos da pergunta e licença, mais `answers` com os registros do WF04 |
| WF10 | `processed/result_stackoverflow_{source_id_do_primeiro_item}.json` e `processed/routing/{fila}/result_stackoverflow_{routing.destination}_{source_id_do_primeiro_item}_{execution_id}.json`; cada item representa uma resposta, mas a conversão agrupa os itens recebidos em um arquivo por ramo |

No WF04, a tag do nome do arquivo substitui `;`, `#`, `.` e `+` por `_`. Perguntas sem ID, título, corpo ou link são descartadas no WF02; licenças sem ID são descartadas no WF03. O WF04 descarta respostas sem campo `title_answer_` com sufixo numérico, incluindo registros cujo sufixo seja `unknown`. O HTML dos corpos é preservado.

O WF08 seleciona chaves que contém `sample_stackoverflow` e terminam em `.json`, sem separar tag, período ou execução. Agrupa por ID e acumula respostas sem deduplicação; pode gerar registros sem pergunta. O nome de saída depende da primeira chave selecionada e remove o primeiro háfen da parte da tag (exemplo: `raw/stackoverflow_artificialintelligence.json`).

O WF05 compacta os objetos listados de todo o bucket, incluindo outras fontes e pastas; não entrega somente dados do Stack Exchange. Retorna HTTP 200 com `Content-Type: application/zip`, `Content-Disposition: attachment` e `Cache-Control: no-store`.

Os nomes da coleta, do WF08 e do resultado principal do WF10 não incluem identificador de execução; novas execuções podem sobrescrever objetos existentes. Os arquivos das filas de roteamento do WF10 incluem o identificador da primeira pergunta recebida pelo ramo e o de execução, sem identificar individualmente cada resposta.

## 4. Triagem atual — WF10

O WF10 lê `raw/stackoverflow*.json`, mantém perguntas com `body_question` preenchido e `is_answered_question=true`, mapeia os campos e aplica `Limit=10` antes do agente. O filtro temporário `Filter1`, configurado para `source_id=79965487`, está desativado. O agente recebe até dez perguntas por execução, cada uma com seu array de respostas; não há mecanismo de avanço para as próximas perguntas. O limite controla perguntas, não a quantidade de respostas avaliadas.

O `AI Agent` usa título e corpo da pergunta como contexto e avalia cada resposta, sem classificar a pergunta. O `System Message` determina avaliação direta, sem ferramentas; a versão atual não utiliza o nó `SKill Router Classification`. A saída estruturada do agente contém `source_id`, `source=stackoverflow` e `answers`, com:

| Campo por resposta | Tipo / valores |
| --- | --- |
| `answer_id` | Inteiro positivo, preservado da entrada |
| `original_language` | `pt`, `es`, `en` ou `other` |
| `sentiment` | `Excited`, `Happy`, `Neutral`, `Disappointed` ou `Angry` |
| `strength` | Número de 0 a 1: intensidade do sentimento |
| `confidence` | Número de 0 a 1: confiança na classificação |
| `content_type` | `technical_answer`, `job_achievement`, `testimonial`, `technical_question`, `course_feedback`, `debate` ou `noise` |
| `topics` | Até cinco strings não vazias, sem duplicatas |
| `relevance_score` | Inteiro de 0 a 100: relevância editorial |
| `summary` | Resumo não vazio em português brasileiro |
| `suggested_route` | `success_case`, `faq`, `newsletter_only`, `moderation` ou `discard` |
| `needs_human_review` | Booleano: necessidade de revisão humana |
| `assessment_note` | Justificativa editorial não vazia em português brasileiro |

O `Structured Output Parser` exige todos os campos listados e rejeita propriedades adicionais; a correção automática está desativada. O modelo principal é `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, com temperatura zero e formato JSON; o fallback configurado é `google/gemma-4-31b-it`. O prompt reforça que `content_type` e `suggested_route` são campos distintos e que `faq` não é uma categoria de conteúdo. O nó `Merge Classification` exige correspondência de `source_id`, fonte e conjunto de IDs de respostas, rejeita IDs duplicados e valida tipos, categorias e escalas. Preserva os dados originais, incorpora `original_language`, `sentiment`, `strength` e `confidence` na raiz de cada resposta e agrupa os outros sete campos em `answers[].editorial`. Também rejeita tópicos repetidos e conflitos com avaliações já existentes no original. `noise` exige rota `discard`; `moderation` exige revisão humana.

Após as validações, o `Merge Classification` produz um item por resposta, preserva o contexto da pergunta e `source_file`, mantém apenas a resposta correspondente em `answers` e copia `answer_id`, `suggested_route` e `needs_human_review` para a raiz, no mesmo nível de `source_id`. As decisões continuam em `answers[0].editorial`, e o ID permanece em `answers[0].answer_id`. O merge rejeita um array de respostas vazio e conflitos com esses metadados na raiz do original.

O `If Human Review` consulta `$json.needs_human_review`: quando verdadeiro, define `routing.destination=human_review` e `routing.status=pending_review`. Caso contrário, o Switch `Editorial Route` consulta `$json.suggested_route` e compara as cinco rotas. `success_case`, `faq` e `newsletter_only` recebem status `pending_generation`; esta última usa destino `newsletter`. `discard` recebe status `discarded`. O caminho `moderation` define destino `human_review` e status `pending_review`, mas avaliações válidas dessa categoria são interceptadas antes pelo `If`, pois exigem revisão humana. O fallback define destino `human_review` e status `invalid_route`. As rotas produzidas pelo agente são recomendações; o fluxo não gera textos finais de FAQ, newsletter ou redes sociais.

## 5. Respostas e falhas

WF02, WF03, WF04 e WF08 configuram HTTP 200 após o upload, com JSON contendo `status: "success"` e `message`. Não retornam contagem nem `download_url`. WF08 também configura o cabeçalho `filename`. O sucesso HTTP não comprova completude ou qualidade dos dados.

No WF10, os caminhos de conversão e upload do resultado principal e das filas estão conectados ao `Merge` e ao `Respond to Webhook`, configurado para HTTP 200 com `status: "success"` e mensagem genérica. A inclusão das mensagens específicas de roteamento está planejada. A execução manual 10216 (09/11/2026, 16h31–16h33, America/Sao_Paulo), com duração aproximada de 2min27s, processou dez perguntas e 16 respostas: 12 para FAQ, três para descarte e uma para revisão humana, recomendada como `moderation`. Chegou ao `Respond to Webhook` com quatro uploads bem-sucedidos. A execução 10212 processou 15 respostas da pergunta `79965487`: 11 para FAQ, duas para newsletter e duas para descarte, também com quatro uploads e conclusão. Esses resultados não comprovam a chamada ao webhook de produção nem a qualidade editorial de todas as avaliações.

WF02, WF03 e WF04 respondem HTTP 400 para parâmetros inválidos:

```json
{
  "status": "error",
  "message": "Parâmetros de busca inválidos.",
  "details": "Descrição da validação que falhou."
}
```

Não há contrato uniforme de erro para falhas de API externa, OCI, modelo ou ausência de itens. As retentativas são configuradas apenas em alguns nós; não assumir repetição em todo o fluxo. Após falha de comunicação, verificar a execução antes de reenviar a chamada, pois arquivos podem ter sido gravados.

Manter o bucket privado, usar HTTPS e guardar a chave fora do código e dos logs. Validar os arquivos baixados e as quantidades efetivas; esta revisão não reproduziu os testes históricos de produção.

## 6. Persistência no bucket

Os arquivos são persistidos no bucket `communitylab-assets`. WF02, WF03 e WF04 gravam os dados coletados na raiz do bucket para consolidação pelo WF08. O WF08 grava o resultado em `raw/`, de onde o WF10 lê os dados para triagem. No WF10, as execuções 10212 e 10216 registraram sucesso nos uploads em `processed/` e nas filas utilizadas de `processed/routing/`; a conferência direta do conteúdo dos objetos baixados permanece pendente nesta revisão.

| Workflow produtor | Local de persistência | Consumidor e finalidade |
| --- | --- | --- |
| WF02 | Raiz do bucket: `sample_{site}-questions_{tagged}.json` | WF08: consolidação das perguntas |
| WF03 | Raiz do bucket: `sample_{site}-questions-licenses_{tagged}.json` | WF08: associação das licenças às perguntas |
| WF04 | Raiz do bucket: `sample_{site}-answers_{tagged_normalizada}.json` | WF08: associação das respostas às perguntas |
| WF08 | `raw/{nome_derivado}.json` | WF10: leitura dos registros consolidados para triagem |
| WF10 | `processed/result_stackoverflow_{source_id_do_primeiro_item}.json` e arquivos em `processed/routing/{fila}/` | Aplicação: consumo previsto dos lotes de resultados e das filas editoriais; uploads validados em execução manual |

As filas configuradas são `human_review`, `success_case`, `faq`, `newsletter`, `moderation`, `discard` e `fallback`. A pasta identifica o ramo executado; nos ramos de moderação e fallback, `routing.destination` é `human_review`. Os arquivos das filas usam o nome `result_stackoverflow_{routing.destination}_{source_id_do_primeiro_item}_{execution_id}.json`. Cada conversão reúne os itens recebidos em um único arquivo. Na execução 10216, o arquivo principal foi `result_stackoverflow_79857625.json`, embora o lote contivesse dez perguntas; a FAQ gerou `result_stackoverflow_faq_79857625_10216.json`, com 12 itens enviados à conversão. Portanto, o ID no nome não deve ser usado para inferir que o arquivo contém apenas aquela pergunta. Para ampliar o processamento, adotar nomes de lote ou agrupar explicitamente por pergunta antes da conversão.

O WF05 também lê os arquivos do bucket para disponibilizá-los em um ZIP ao solicitante; não persiste um novo arquivo no bucket. Os critérios de seleção dos arquivos pelos workflows estão descritos nas seções 3 e 4.

## 7. Pendências para concluir o MVP

- Validar uma chamada ao webhook autenticado e o caminho de caso de sucesso; múltiplas perguntas, respostas com destinos diferentes e revisão humana já foram exercitadas em execução manual.
- Conferir diretamente o conteúdo e as quantidades dos arquivos baixados; alinhar os nomes dos arquivos ao agrupamento por lote ou implementar agrupamento explícito por pergunta.
- Validar o agente, o parser e o merge com múltiplas respostas, IDs divergentes, entradas inválidas e conteúdo com instruções embutidas; medir a qualidade das avaliações sem presumir que o JSON válido comprova acurácia.
- Rever o limite de dez perguntas e a seleção de arquivos por coleta para evitar reprocessamento e mistura de conjuntos; repetir o lote maior e os casos anteriormente incompatíveis antes de ampliar o uso.
- Tratar explicitamente ausência de itens elegíveis, respostas vazias e falhas de modelo ou OCI. Atualizar as mensagens de roteamento do `Respond to Webhook` no momento planejado.
