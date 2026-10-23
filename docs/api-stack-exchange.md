# Contrato de API — Stack Exchange

**Projeto:** CommunityLab  
**Base URL:** `https://bot.rsa.ia.br`  
**Versão:** 1.0  
**Formato:** JSON UTF-8 e download de arquivo JSON  
**Autenticação:** Header Auth

## 1. Visão geral

A integração disponibiliza duas operações:

| Operação | Método | Endpoint |
|---|---|---|
| Coletar, integrar e disponibilizar dados | POST | `/webhook/wf04-integracao-stack-exchange` |
| Baixar o JSON enriquecido | GET | `/webhook/wf05-download-stack-exchange` |

O fluxo de processamento utiliza os workflows [WF02](../n8n/workflows/wf02_coleta-stack-exchange-integrada.json) e [WF03](../n8n/workflows/wf03_coleta-StackExchange-licenses-integrada.json) para obter os dados do Stack Exchange, integra as coleções e grava o resultado no OCI Object Storage.

O arquivo gerado é armazenado no bucket privado `communitylab-assets`, no caminho:

`samples/stackexchange-questions-enriched.json`

O [WF04](../n8n/workflows/wf04_integração-StackExchange.json) retorna a URL do WF05 para que o sistema consumidor possa baixar o arquivo.

## 2. Autenticação

As duas operações exigem autenticação por cabeçalho HTTP.

| Campo | Valor |
|---|---|
| Nome do cabeçalho | `communitylab-api-key` |
| Valor | Chave de API fornecida para o consumidor |

Exemplo de cabeçalho:

```http
communitylab-api-key: <SUA_CHAVE_DE_API>
```

A chave deve ser armazenada em um mecanismo seguro de gestão de segredos. Não deve ser incluída no código-fonte, no repositório Git ou em logs.

O consumidor deve enviar o cabeçalho nas duas operações, inclusive no download do arquivo.

## 3. Endpoint WF04 — Integração Stack Exchange

### Requisição

**Método:** `POST`

**URL:**

`https://bot.rsa.ia.br/webhook/wf04-integracao-stack-exchange`

**Content-Type:** `application/json`

### Parâmetros de entrada

| Campo | Tipo | Valor padrão | Descrição |
|---|---|---|---|
| `tagged` | string | `artificial-intelligence` | Tag utilizada para filtrar perguntas |
| `fromdate` | integer | `1760929200` | Timestamp Unix que define o início do período de coleta |
| `pagesize` | integer | `100` | Quantidade solicitada por página à API de origem |

Os valores padrão são os configurados no workflow. Os limites efetivamente aceitos para cada parâmetro devem respeitar as regras da API do Stack Exchange.

### Exemplo de requisição

```http
POST /webhook/wf04-integracao-stack-exchange HTTP/1.1
Host: bot.rsa.ia.br
Content-Type: application/json
communitylab-api-key: <SUA_CHAVE_DE_API>
```

Corpo JSON:

```json
{
  "tagged": "artificial-intelligence",
  "fromdate": 1760929200,
  "pagesize": 100
}
```

### Resposta de sucesso

**HTTP:** `200 OK`

**Content-Type:** `application/json`

Exemplo de resposta observada em produção:

```json
{
  "status": "success",
  "message": "Coleta integrada concluída e arquivo enriquecido disponibilizado no bucket OCI.", 
  "file": "samples/stackexchange-questions-enriched.json",
  "records": 151,
  "download_url": "https://bot.rsa.ia.br/webhook/wf05-download-stack-exchange"
}
```

O campo `records` representa a quantidade de registros produzidos pela execução. Esse valor pode variar entre coletas.

| Campo | Tipo | Significado |
|---|---|---|
| `status` | string | Estado da execução |
| `message` | string | Mensagem de resultado |
| `file` | string | Caminho do arquivo no bucket OCI |
| `records` | integer | Quantidade de registros integrados |
| `download_url` | string | URL para baixar o arquivo produzido |

A URL de download não contém a chave de autenticação. O consumidor deve enviá-la no cabeçalho da requisição seguinte.

## 4. Endpoint [WF05](../n8n/workflows/wf05_download-JSON-enriquecido.json) — Download JSON Enriquecido

### Requisição

**Método:** `GET`

**URL:**

`https://bot.rsa.ia.br/webhook/wf05-download-stack-exchange`

O endpoint entrega o arquivo produzido pelo WF04. Não recebe corpo JSON nem parâmetros obrigatórios de consulta.

### Exemplo de requisição

```http
GET /webhook/wf05-download-stack-exchange HTTP/1.1
Host: bot.rsa.ia.br
communitylab-api-key: <SUA_CHAVE_DE_API>
```

### Resposta de sucesso

**HTTP:** `200 OK`

Cabeçalhos configurados:

```http
Content-Type: application/json
Content-Disposition: attachment; filename="stackexchange-questions-enriched.json"
Cache-Control: no-store
```

O corpo da resposta é o próprio arquivo JSON, não um objeto contendo uma URL ou uma lista encapsulada em outro campo.

O arquivo contém uma coleção de registros enriquecidos, incluindo campos como `source_id`, título, conteúdo, tags, pontuação, datas e `content_license`, conforme os dados retornados pelas fontes.

## 5. Exemplo de consumo em PowerShell

O exemplo executa a coleta, lê a URL de download retornada e baixa o arquivo utilizando a mesma chave de API.

A variável `$apiKey` deve ser previamente definida de forma segura pelo ambiente consumidor.

```powershell
$headers = @{
    "communitylab-api-key" = $apiKey
}

$body = @{
    tagged   = "artificial-intelligence"
    fromdate = 1760929200
    pagesize = 100
} | ConvertTo-Json

# 1. Executar a integração
$result = Invoke-RestMethod `
    -Method Post `
    -Uri "https://bot.rsa.ia.br/webhook/wf04-integracao-stack-exchange" `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $body `
    -ErrorAction Stop

if ($result.status -ne "success") {
    throw "A integração não retornou status de sucesso."
}

# 2. Baixar o arquivo produzido
$outputFile = Join-Path $HOME "Downloads\stackexchange-questions-enriched.json"

Invoke-WebRequest `
    -Method Get `
    -Uri $result.download_url `
    -Headers $headers `
    -OutFile $outputFile `
    -ErrorAction Stop

# 3. Validar o JSON baixado
$data = Get-Content $outputFile -Raw | ConvertFrom-Json

Write-Host "Arquivo:" $outputFile
Write-Host "Registros retornados pelo WF04:" $result.records
Write-Host "Registros encontrados no arquivo:" @($data).Count
```

O exemplo utiliza o PowerShell para demonstrar a sequência de chamadas. Outros sistemas podem implementar o mesmo contrato usando HTTP e JSON.

## 6. Tratamento de erros

O consumidor deve tratar separadamente erros de transporte, autenticação e processamento.

| Situação | Conduta recomendada |
|---|---|
| `401` ou `403` | Verificar a credencial e o cabeçalho de autenticação |
| Erro de resolução DNS ou conexão | Registrar a falha e realizar novas tentativas controladas |
| Resposta HTTP diferente de sucesso | Registrar status e detalhes seguros da resposta |
| JSON inválido | Interromper o processamento e registrar a ocorrência |
| Quantidade de registros divergente | Investigar a execução e o conteúdo efetivamente baixado |

Não se deve presumir que toda falha resulte em um código HTTP específico sem validar o comportamento efetivo do workflow.

Se ocorrer uma falha de comunicação após o envio do POST, o consumidor deve considerar que o estado da execução pode ser desconhecido antes de repetir a solicitação. Uma nova execução pode produzir outro arquivo e substituir o anterior.

## 7. Segurança e operação

- Manter o bucket OCI privado.
- Utilizar HTTPS em todas as requisições.
- Proteger a chave de API e limitar seu compartilhamento.
- Não registrar chaves, cabeçalhos secretos ou conteúdo sensível nos logs.
- Validar o JSON baixado antes de utilizá-lo.
- Não assumir uma quantidade fixa de registros.
- Considerar que o nome do arquivo é estável e que novas execuções podem substituir seu conteúdo.

## 8. Validação realizada

Na validação de produção de 23/10/2026:

- O WF04 retornou `status: success`.
- A resposta incluiu `download_url`.
- O WF04 informou 151 registros.
- O WF05 entregou o arquivo com HTTP 200.
- O arquivo baixado foi interpretado como JSON válido e continha 151 registros.

Esses resultados comprovam o funcionamento do fluxo no momento do teste. Não representam garantia de disponibilidade contínua ou de uma quantidade fixa de registros em execuções futuras.

## 9. Pontos para evolução

Antes de declarar o contrato como uma API versionada e estável, recomenda-se documentar e validar formalmente:

- esquema completo dos registros retornados;
- limites e validações dos parâmetros;
- códigos e formatos de erro de cada endpoint;
- política de repetição e identificação das execuções;
- estratégia de versionamento do contrato;
- prazo de validade do arquivo e comportamento em execuções simultâneas.
