# Contrato de API — Stack Exchange

**Projeto:** CommunityLab
**Workflow:** [wf10-triagem-llm-router_stackexchange](../../n8n/workflows/wf10_triagem-llm-router_stackexchange.json)
**Identificador:** `fPkrXUK7Kre97d89`
**Versão documental:** 1.2 - MVP\
**Configuração consultada:** 11/11/2026 — export local; sem execução nesta revisão\
**Base URL:** `https://bot.rsa.ia.br`  
**Método:** `POST`
**Autenticação do webhook:** Header Auth, credencial `Hackathon CommunityLab`\
**Resposta:** JSON; os arquivos resultantes são persistidos na OCI.

**Estado do WF10:** implementado no arquivo local, com `active=true`, ID `fPkrXUK7Kre97d89` e versão `e4b52c9a-c85e-4cde-b32e-62c586fe0f67`. Esse atributo não comprova que a mesma versão esteja publicada no servidor. A configuração atual limita a entrada a cinco perguntas e agrupa as respostas em arquivos por lote/ramo, com nomes baseados na fonte e na tag. Os testes manuais de 09/11/2026 registrados anteriormente pertencem a outra versão e não validam esta configuração.

## 1. Operações

| Workflow | Método e caminho relativo | Resultado |
| --- | --- | --- |
| [WF02](../../n8n/workflows/wf02_coleta-stack-exchange-questions-integrada.json) | `POST wf02-coleta-stack-exchange` | Coleta e sanitiza perguntas; grava JSON na OCI |
| [WF03](../../n8n/workflows/wf03_coleta-stack-exchange-licenses-integrada.json) | `POST wf03-coleta-stack-exchange-licenses` | Coleta licenças das perguntas; grava JSON na OCI |
| [WF04](../../n8n/workflows/wf04_coleta-stack-exchange-answer-integrada.json) | `POST wf04-coleta-stack-exchange-answers` | Busca perguntas e coleta suas respostas em lotes de até 100 IDs; grava JSON na OCI |
| [WF05](../../n8n/workflows/wf05_download-bucket-OCI.json) | `GET wf05-download-bucket-OCI` | Baixa os objetos listados no bucket e devolve um ZIP |
| [WF08](../../n8n/workflows/wf08_merge-stackexchange-data.json) | `GET wf08_merge-stackexchange-data` | Combina perguntas, licenças e respostas por `source_id`; grava em `raw/` |
| [WF10](../../n8n/workflows/wf10_triagem-llm-router_stackexchange.json) | `POST wf10_triagem-llm-router_stackexchange` | Avalia idioma, sentimento e atributos editoriais; roteia cada resposta e configura persistência em `processed/` e nas filas editoriais |

Em todos os fluxos a autenticação é `Header Auth`. Enviar `communitylab-api-key: <SUA_CHAVE_DE_API>`, conforme [credenciais n8n](./n8n-credentials.md).

As operações são independentes: executar WF02, WF03 e WF04, com os mesmos parâmetros, para coletar os dados e salvar no bucket da OCI. Já WF08 unifica os dados em um único `json`, salvando-o também no bucket, e WF10 recupera esse arquivo para avaliá-lo. WF05 serve para baixar os arquivos localmente. Não há encadeamento automático entre esses workflows.

## 2. Entrada da coleta — WF02, WF03 e WF04

Enviar um objeto JSON no corpo do POST, com `Content-Type: application/json`. Campos omitidos ou nulos usam os padrões abaixo.

| Campo | Padrão | Validação implementada |
| --- | --- | --- |
| `tagged` | `artificial intelligence` | String não vazia, até 200 caracteres; padrão `^[a-zA-Z0-9.+#_;-]+$` |
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

WF05 não recebe filtro de download. WF08 e WF10 usam `source=stackoverflow`, por padrão, e extensão `.json` fixos nos nós de configuração; o corpo da requisição não altera esses valores.

## 3. Arquivos e dados

Todos os arquivos são armazenados no bucket `communitylab-assets`, acessado pelos nós S3.

| Etapa | Chave do objeto / estrutura |
| --- | --- |
| WF02 | `sample_{site}-questions_{tagged}.json`: perguntas com `source_id` string, título, corpo HTML, autor, link, tags e métricas com sufixo `_question` |
| WF03 | `sample_{site}-licenses_{tagged}.json`: `source_id` e `content_license_question` (pode ser `null`) |
| WF04 | `sample_{site}-answers_{tagged_normalizada}.json`: `source_id` string, `answer_id` e campos dinâmicos como `body_answer_{account_id}`, autor, licença e métricas |
| WF08 | `raw/{nome_derivado}.json`: um registro por `source_id`, campos da pergunta e licença, mais `answers` com os registros do WF04 |
| WF10 | `processed/result_stackoverflow_{tagged}.json` e `processed/routing/{fila}/result_stackoverflow_{routing.destination}_{tagged}_{execution_id}.json`; cada item representa uma resposta, mas a conversão agrupa os itens recebidos em um arquivo por ramo |

No WF04, a tag do nome do arquivo substitui `;`, `#`, `.` e `+` por `_`. Perguntas sem ID, título, corpo ou link são descartadas no WF02; licenças sem ID são descartadas no WF03. O WF04 descarta respostas sem campo `title_answer_` com sufixo numérico, incluindo registros cujo sufixo seja `unknown`. O HTML dos corpos é preservado.

O WF08 seleciona chaves que contêm `sample_stackoverflow` e terminam em `.json`, sem separar tag, período ou execução. Agrupa por ID e acumula respostas sem deduplicação; pode gerar registros sem pergunta. O nome de saída depende da primeira chave selecionada e remove o primeiro hífen da parte da tag (exemplo: `raw/stackoverflow_artificialintelligence.json`).

O WF05 compacta os objetos listados de todo o bucket, incluindo outras fontes e pastas; não entrega somente dados do Stack Exchange. Retorna HTTP 200 com `Content-Type: application/zip`, `Content-Disposition: attachment` e `Cache-Control: no-store`.

Os nomes da coleta, do WF08 e do resultado principal do WF10 não incluem identificador de execução; novas execuções podem sobrescrever objetos existentes. Os arquivos das filas do WF10 incluem fonte, destino, tag sem espaço e identificador de execução, sem identificar individualmente cada pergunta ou resposta.

## 4. Triagem atual — WF10

O WF10 lista o prefixo `raw/` no bucket e seleciona chaves que começam com `raw/stackoverflow` e terminam em `{tagged}.json`, sem diferenciar maiúsculas de minúsculas. Os valores internos são `source=stackoverflow`, `file_type=.json` e `tag=artificial intelligence`; a expressão `tag.replace(' ', '')` remove espaço para seleção e nomes de saída. O corpo do POST não altera essa configuração. A seleção não separa período ou execução e pode corresponder a mais de um arquivo.

Após download e extração do JSON, `Split Out` separa `data`. O filtro mantém perguntas com `body_question` existente e não vazio e `is_answered_question=true`, com validação flexível de tipos. `Map StackOverflow Fields` prepara contexto e metadados, preserva `answers` e obtém `source_file` da chave do download. O fluxo aplica `Limit=5` antes do agente. 

O filtro temporário `Filter1`, configurado para `source_id=79965487`, está desativado, porque é utilizado somente para avaliação dos dados. 

O agente recebe até cinco perguntas por execução, cada uma com seu array de respostas; não há mecanismo de avanço para as próximas perguntas. O limite controla perguntas, não a quantidade de respostas avaliadas.

### Chamada do webhook

O endpoint configurado é `POST https://bot.rsa.ia.br/webhook/wf10_triagem-llm-router_stackexchange`. Seu uso depende da publicação/ativação no servidor. O endpoint de teste substitui `/webhook/` por `/webhook-test/` e depende da escuta de teste no editor. Há também um gatilho manual, conectado à mesma preparação de entrada.

```powershell
$headers = @{ 'communitylab-api-key' = $env:COMMUNITYLAB_API_KEY }
$response = Invoke-RestMethod `
    -Uri 'https://bot.rsa.ia.br/webhook/wf10_triagem-llm-router_stackexchange' `
    -Method POST `
    -Headers $headers `
    -ContentType 'application/json; charset=utf-8' `
    -Body '{}' `
    -TimeoutSec 300 `
    -ErrorAction Stop
$response | ConvertTo-Json -Depth 20
```

O corpo vazio é intencional: os dados são lidos da OCI, não enviados nesta chamada. O exemplo não foi executado nesta revisão.

### Avaliação e contrato por resposta

O `AI Agent` usa título e corpo da pergunta como contexto e avalia cada resposta, sem classificar a pergunta. O `System Message` determina avaliação direta, sem ferramentas; a versão atual não utiliza o nó `SKill Router Classification`. A saída estruturada do agente contém `source_id`, `source=stackoverflow` e `answers`, com:

| Campo por resposta | Tipo / valores |
| --- | --- |
| `answer_id` | Inteiro positivo, preservado da entrada |
| `original_language` | `pt`, `es`, `en` ou `other` |
| `sentiment` | `Excited`, `Happy`, `Neutral`, `Disappointed` ou `Angry` |
| `strength` | Número de 0 a 1: intensidade do sentimento |
| `confidence` | Número de 0 a 1: confiança na classificação |
| `content_type` | `technical_answer`, `job_achievement`, `testimonial`, `technical_question`, `course_feedback`, `debate` ou `noise` |
| `topics` | Até cinco strings não vazias, sem duplicatas; o prompt solicita português brasileiro |
| `relevance_score` | Inteiro de 0 a 100: relevância editorial |
| `summary` | Resumo não vazio em português brasileiro |
| `suggested_route` | `success_case`, `faq`, `newsletter_only`, `moderation` ou `discard` |
| `needs_human_review` | Booleano: necessidade de revisão humana |
| `assessment_note` | Justificativa editorial não vazia em português brasileiro |

O `Structured Output Parser` exige todos os campos listados e rejeita propriedades adicionais; a correção automática está desativada. O modelo principal é `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, com temperatura zero e formato JSON; o fallback configurado é `google/gemma-4-31b-it`. O prompt reforça que `content_type` e `suggested_route` são campos distintos e que `faq` não é uma categoria de conteúdo. 

O nó `Merge Classification` exige correspondência de `source_id`, fonte e conjunto de IDs de respostas, rejeita IDs duplicados e valida tipos, categorias e escalas. Preserva os dados originais, incorpora `original_language`, `sentiment`, `strength` e `confidence` na raiz de cada resposta e agrupa os outros sete campos em `answers[].editorial`. Também rejeita tópicos repetidos e conflitos com avaliações já existentes no original. `noise` exige rota `discard`; `moderation` exige revisão humana.

Após as validações, o `Merge Classification` produz um item por resposta, preserva o contexto da pergunta e `source_file`, mantém apenas a resposta correspondente em `answers` e copia `answer_id`, `suggested_route` e `needs_human_review` para a raiz, no mesmo nível de `source_id`. As decisões continuam em `answers[0].editorial`, e o ID permanece em `answers[0].answer_id`. O merge rejeita um array de respostas vazio e conflitos com esses metadados na raiz do original.

O `If Human Review` consulta `$json.needs_human_review`: quando verdadeiro, define `routing.destination=human_review` e `routing.status=pending_review`. Caso contrário, o Switch `Editorial Route` consulta `$json.suggested_route` e compara as cinco rotas. `success_case`, `faq` e `newsletter_only` recebem status `pending_generation`; esta última usa destino `newsletter`. `discard` recebe status `discarded`. O caminho `moderation` define destino `human_review` e status `pending_review`, mas avaliações válidas dessa categoria são interceptadas antes pelo `If`, pois exigem revisão humana. O fallback define destino `human_review` e status `invalid_route`. As rotas produzidas pelo agente são recomendações; o fluxo não gera textos finais de FAQ, newsletter ou redes sociais.

## 5. Respostas e falhas

WF02, WF03, WF04 e WF08 configuram HTTP 200 após o upload, com JSON contendo `status: "success"` e `message`. Não retornam contagem nem `download_url`. WF08 também configura o cabeçalho `filename`. O sucesso HTTP não comprova completude ou qualidade dos dados.

No WF10, os oito caminhos de upload (resultado principal e sete filas) estão conectados ao `Merge`, configurado com oito entradas, e depois ao `Respond to Webhook`. A resposta configurada é HTTP 200 com o JSON abaixo, sem contagens, destinos, nomes de arquivos ou URL de download. A conclusão com ramos sem itens precisa ser verificada em execução da versão atual.

```json
{
  "status": "success",
  "message": "Análise de sentimento feito e arquivo disponibilizado no bucket OCI."
}
```

WF02, WF03 e WF04 respondem HTTP 400 para parâmetros inválidos:

```json
{
  "status": "error",
  "message": "Parâmetros de busca inválidos.",
  "details": "Descrição da validação que falhou."
}
```

No WF10, `AI Agent` e `Merge Classification` usam `continueErrorOutput`, com as saídas de erro conectadas diretamente a `Prepare Error`. Esse nó mantém apenas `status=error`, `error=triage_failed`, `message="Não foi possível concluir ou validar a classificação do lote."` e `execution_id`, obtido de `$execution.id`. `Screening Error Message` devolve esses campos como JSON com HTTP 502. A configuração foi conferida no export local; os cenários de falha ainda precisam de validação em execução.

### Nós de tratamento de erro do WF10

| Nó | Entrada e comportamento | Saída |
| --- | --- | --- |
| `AI Agent` | Falha que chega à saída de erro do agente, inclusive quando não consegue obter uma classificação válida com o fallback configurado | Saída de erro para `Prepare Error`; saída de sucesso para `Merge Classification` |
| `Merge Classification` | Erro lançado ao validar ou recompor a classificação | Saída de erro para `Prepare Error`; saída de sucesso para persistência principal e `If Human Review` |
| `Prepare Error` | Edit Fields com quatro campos String; sem inclusão dos demais campos de entrada | Um objeto de erro sem conteúdo original, detalhes internos ou stack trace, enviado a `Screening Error Message` |
| `Screening Error Message` | Respond to Webhook com `Respond With=JSON` e corpo `={{ $json }}` | HTTP `502` com o objeto preparado |

As duas saídas de erro chegam diretamente a `Prepare Error`, sem um nó Merge intermediário. O objeto de resposta configurado é:

```json
{
  "status": "error",
  "error": "triage_failed",
  "message": "Não foi possível concluir ou validar a classificação do lote.",
  "execution_id": "<ID da execução n8n>"
}
```

Esse caminho atende às falhas encaminhadas pelos dois nós de triagem. Não é a fila editorial `human_review` nem o ramo `Fallback` do Switch: estes recebem classificações processadas pelo caminho de sucesso. Falhas de listagem, download, extração, conversão ou upload não possuem conexão com `Prepare Error` nesta versão.

Para homologar os novos nós, verificar separadamente uma falha do agente após o fallback e uma classificação rejeitada por `Merge Classification`. Em chamadas pelo webhook, conferir HTTP 502, os quatro campos acima e o vínculo de `execution_id` com a execução registrada. Em um lote com itens válidos e inválidos, verificar também qual resposta HTTP é emitida e quais objetos foram persistidos; os caminhos de sucesso e erro não possuem uma consolidação única de estado do lote.

Não há contrato uniforme de erro para falhas de API externa, OCI ou ausência de itens. No WF10 exportado, nenhum nó declara `retryOnFail`; o fallback de modelo está habilitado no agente, mas não equivale a retentativas de todo o fluxo. Após falha de comunicação, é necessário verificar a execução antes de reenviar a chamada, pois arquivos podem ter sido gravados. O upload principal e os uploads das filas não formam uma transação, e não há rollback configurado. O caminho HTTP 502 não desfaz uploads anteriores nem garante interrupção dos demais itens do lote.

Manter o bucket privado, usar HTTPS e guardar a chave fora do código e dos logs. Validar os arquivos baixados e as quantidades efetivas; esta revisão não reproduziu os testes históricos de produção.

## 6. Persistência no bucket

Os arquivos são persistidos no bucket `communitylab-assets`. WF02, WF03 e WF04 gravam os dados coletados na raiz do bucket para consolidação pelo WF08. O WF08 grava o resultado em `raw/`, de onde o WF10 lê os dados para triagem. A configuração local do WF10 prevê os uploads abaixo; sua execução e o conteúdo dos objetos não foram verificados nesta revisão.

| Workflow produtor | Local de persistência | Consumidor e finalidade |
| --- | --- | --- |
| WF02 | Raiz do bucket: `sample_{site}-questions_{tagged}.json` | WF08: consolidação das perguntas |
| WF03 | Raiz do bucket: `sample_{site}-questions-licenses_{tagged}.json` | WF08: associação das licenças às perguntas |
| WF04 | Raiz do bucket: `sample_{site}-answers_{tagged_normalizada}.json` | WF08: associação das respostas às perguntas |
| WF08 | `raw/{nome_derivado}.json` | WF10: leitura dos registros consolidados para triagem |
| WF10 | `processed/result_stackoverflow_artificialintelligence.json` e arquivos em `processed/routing/{fila}/` | Aplicação: consumo previsto dos lotes de resultados e das filas editoriais |

As filas configuradas são `human_review`, `success_case`, `faq`, `newsletter`, `moderation`, `discard` e `fallback`. A pasta identifica o ramo executado; nos ramos de moderação e fallback, `routing.destination` é `human_review`. Os arquivos das filas usam o nome `result_stackoverflow_{routing.destination}_artificialintelligence_{execution_id}.json`. Cada conversão reúne os itens recebidos em um único arquivo, podendo incluir respostas de perguntas diferentes. Os IDs individuais devem ser lidos dos registros, não do nome do arquivo.

O resultado principal é produzido diretamente após `Merge Classification`, antes de adicionar `routing.destination` e `routing.status`. Ele contém as classificações e os metadados de controle na raiz de cada item. As cópias encaminhadas às filas acrescentam `routing`. O arquivo principal é sobrescrito em novas execuções para a mesma fonte/tag; as filas incluem o ID da execução. Não há marcação dos arquivos de entrada como processados, deduplicação entre execuções ou remoção de resultados antigos.

O WF05 também lê os arquivos do bucket para disponibilizá-los em um ZIP ao solicitante; não persiste um novo arquivo no bucket. Os critérios de seleção dos arquivos pelos workflows estão descritos nas seções 3 e 4.

## 7. Limitações do MVP

- Rever o limite de cinco perguntas e a seleção de arquivos por coleta para evitar reprocessamento e mistura de conjuntos; repetir o lote maior e os casos anteriormente incompatíveis antes de ampliar o uso.
- Homologar o caminho HTTP 502 de falhas do agente e de validação, incluindo lotes com sucesso parcial. O caminho está configurado, mas não foi executado nesta revisão.
- Tratar explicitamente ausência de itens elegíveis e falhas de leitura ou gravação na OCI. Um array de respostas vazio é rejeitado por `Merge Classification` e encaminhado ao tratamento de erro; ausência de itens antes do agente ainda não tem resposta específica. Definir se a resposta HTTP deve incluir contagens, destinos e chaves dos objetos.
