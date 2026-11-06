# Contrato de API — Stack Exchange

**Projeto:** CommunityLab — MVP  
**Base dos webhooks:** `https://bot.rsa.ia.br/webhook/`  
**Formato:** JSON UTF-8; WF05 entrega ZIP.  
**Referência:** análise estática dos workflows exportados; execução em produção não validada nesta revisão.

**Estado do WF10: em desenvolvimento (06/11/2026).** A avaliação editorial já foi incorporada ao agente, ao parser e ao merge, mas o roteamento e as conexões de persistência ainda estão incompletos. Este documento descreve a exportação local; não representa um contrato estável nem comprova execução de ponta a ponta.

## 1. Operações

| Workflow | Método e caminho relativo | Resultado |
| --- | --- | --- |
| [WF02](../../n8n/workflows/wf02_coleta-stack-exchange-questions-integrada.json) | `POST wf02-coleta-stack-exchange` | Coleta e sanitiza perguntas; grava JSON na OCI |
| [WF03](../../n8n/workflows/wf03_coleta-stack-exchange-licenses-integrada.json) | `POST wf03-coleta-stack-exchange-licenses` | Coleta licenças das perguntas; grava JSON na OCI |
| [WF04](../../n8n/workflows/wf04_coleta-stack-exchange-answer-integrada.json) | `POST wf04-coleta-stack-exchange-answers` | Busca perguntas e coleta suas respostas em lotes de até 100 IDs; grava JSON na OCI |
| [WF05](../../n8n/workflows/wf05_download-bucket-OCI.json) | `GET wf05-download-bucket-OCI` | Baixa os objetos listados no bucket e devolve um ZIP |
| [WF08](../../n8n/workflows/wf08_merge-stackexchange-data.json) | `GET wf08_merge-stackexchange-data` | Combina perguntas, licenças e respostas por `source_id`; grava em `raw/` |
| [WF10](../../n8n/workflows/wf10_triagem-llm-router_stackexchange.json) | `POST wf10_triagem-llm-router_stackexchange` | Avalia idioma, sentimento e atributos editoriais de cada resposta; roteamento e persistência em desenvolvimento |

WF02, WF03, WF04, WF05 e WF08 configuram `Header Auth`. Enviar `communitylab-api-key: <SUA_CHAVE_DE_API>`, conforme [credenciais n8n](./n8n-credentials.md). O webhook do WF10 não configura autenticação no arquivo exportado; proteção externa não foi verificada.

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
| WF10 | Destino configurado: `processed/result_stackoverflow.json`, com classificação e avaliação editorial em cada elemento de `answers`; conexão de upload pendente |

No WF04, a tag do nome do arquivo substitui `;`, `#`, `.` e `+` por `_`. Perguntas sem ID, título, corpo ou link são descartadas no WF02; licenças sem ID são descartadas no WF03. O WF04 descarta respostas sem campo `title_answer_` com sufixo numérico, incluindo registros cujo sufixo seja `unknown`. O HTML dos corpos é preservado.

O WF08 seleciona chaves que contém `sample_stackoverflow` e terminam em `.json`, sem separar tag, período ou execução. Agrupa por ID e acumula respostas sem deduplicação; pode gerar registros sem pergunta. O nome de saída depende da primeira chave selecionada e remove o primeiro háfen da parte da tag (exemplo: `raw/stackoverflow_artificialintelligence.json`).

O WF05 compacta os objetos listados de todo o bucket, incluindo outras fontes e pastas; não entrega somente dados do Stack Exchange. Retorna HTTP 200 com `Content-Type: application/zip`, `Content-Disposition: attachment` e `Cache-Control: no-store`.

Os nomes não incluem identificador de execução; novas execuções podem sobrescrever objetos existentes.

## 4. Triagem atual — WF10

O WF10 lê `raw/stackoverflow*.json`, mantém perguntas com `body_question` preenchido e `is_answered_question=true`, mapeia os campos e aplica `Limit=1` antes do agente. Portanto, processa no máximo uma pergunta por execução, com suas respostas; não há mecanismo de avanço para as próximas perguntas.

O `AI Agent` usa título e corpo da pergunta como contexto e avalia cada resposta, sem classificar a pergunta. O `System Message` determina avaliação direta, sem ferramentas. O nó `SKill Router Classification` permanece na exportação, mas está desconectado do agente. A saída estruturada contém `source_id`, `source=stackoverflow` e `answers`, com:

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

O `Structured Output Parser` exige todos os campos listados e rejeita propriedades adicionais. O nó `Merge Classification` exige correspondência de `source_id`, fonte e conjunto de IDs de respostas, rejeita IDs duplicados e valida tipos, categorias e escalas. Preserva os dados originais, incorpora `original_language`, `sentiment`, `strength` e `confidence` na raiz de cada resposta e agrupa os outros sete campos em `answers[].editorial`. Também rejeita tópicos repetidos e conflitos com avaliações já existentes no original. `noise` exige rota `discard`; `moderation` exige revisão humana.

O roteamento ainda é parcial: `If Human Review` consulta somente `answers[0].editorial.needs_human_review`. O Switch `Editorial Route` contém uma única comparação entre o literal `success_case` e uma string vazia, sem destinos conectados. Não há roteamento individual de todas as respostas. As rotas produzidas pelo agente são recomendações; o fluxo não gera textos finais de FAQ, newsletter ou redes sociais.

## 5. Respostas e falhas

WF02, WF03, WF04 e WF08 configuram HTTP 200 após o upload, com JSON contendo `status: "success"` e `message`. Não retornam contagem nem `download_url`. WF08 também configura o cabeçalho `filename`. O sucesso HTTP não comprova completude ou qualidade dos dados.

No WF10, os nós de upload e resposta de sucesso existem, mas `Convert to File` não está conectado a `Upload a file`. Portanto, o caminho atual de triagem não alcança o upload nem a resposta HTTP 200 configurada. A persistência e a resposta de sucesso dependem da conclusão dessas conexões e de validação em execução.

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

Os arquivos são persistidos no bucket `communitylab-assets`. WF02, WF03 e WF04 gravam os dados coletados na raiz do bucket para consolidação pelo WF08. O WF08 grava o resultado em `raw/`, de onde o WF10 lê os dados para triagem. No WF10, o destino em `processed/` está configurado para consumo futuro pela aplicação, mas a conexão de upload ainda precisa ser concluída.

| Workflow produtor | Local de persistência | Consumidor e finalidade |
| --- | --- | --- |
| WF02 | Raiz do bucket: `sample_{site}-questions_{tagged}.json` | WF08: consolidação das perguntas |
| WF03 | Raiz do bucket: `sample_{site}-questions-licenses_{tagged}.json` | WF08: associação das licenças às perguntas |
| WF04 | Raiz do bucket: `sample_{site}-answers_{tagged_normalizada}.json` | WF08: associação das respostas às perguntas |
| WF08 | `raw/{nome_derivado}.json` | WF10: leitura dos registros consolidados para triagem |
| WF10 | Destino configurado: `processed/result_stackoverflow.json` | Aplicação: consumo previsto; conexão de upload pendente |

O WF05 também lê os arquivos do bucket para disponibilizá-los em um ZIP ao solicitante; não persiste um novo arquivo no bucket. Os critérios de seleção dos arquivos pelos workflows estão descritos nas seções 3 e 4.

## 7. Pendências para concluir o MVP

- Concluir as conexões entre conversão, upload e resposta HTTP e validar a persistência de ponta a ponta.
- Implementar roteamento por resposta, substituindo a consulta exclusiva a `answers[0]`; configurar as cinco rotas, seus destinos e o tratamento de revisão humana e rota inválida.
- Validar o agente, o parser e o merge com múltiplas respostas, IDs divergentes, entradas inválidas e conteúdo com instruções embutidas; medir a qualidade das avaliações sem presumir que o JSON válido comprova acurácia.
- Rever o limite de uma pergunta, a autenticação do WF10 e a seleção de arquivos por coleta para evitar reprocessamento e mistura de conjuntos.
