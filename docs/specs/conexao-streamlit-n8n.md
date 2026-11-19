# Conexão Streamlit → n8n

O [WF12 — Consulta de resultados processados](../../n8n/workflows/wf12_consulta_resultados_processados.json) disponibiliza os arquivos já avaliados da OCI para consumo pelo Streamlit. Relacionado à [issue #20](https://github.com/No-Country-simulation/G10-BRASIL-Equipe-14/issues/20).

## Funcionamento

O workflow valida `source` e `tag`, baixa um arquivo do bucket privado `communitylab-assets`, extrai o JSON e retorna os registros com os metadados da consulta.

```text
Entrada → Validate Request → Request Is Valid → Download a file
        → Extract from File → Prepare Return → Respond to Webhook
```

A chave consultada é `processed/result_{source}_{tag}.json`. O WF12 consulta um arquivo por requisição; não executa coleta ou triagem e não consulta `processed/routing/`.

## Teste manual no editor do n8n

1. Configure as credenciais `OCI Object Storage S3` e `Hackathon CommunityLab` na instância utilizada.
2. No nó `Manual Test`, defina o campo `query` como **Object**:

   ```json
   {
     "source": "stackoverflow",
     "tag": "artificialintelligence"
   }
   ```

3. Execute pelo `Manual Trigger` (`When clicking ‘Execute workflow’`).
4. Confira o binário `data` no download, o array `data` na extração e o envelope final no `Prepare Return`.

Esse teste acontece no editor, mas acessa o bucket real da OCI e exige conexão de rede. Ele verifica o fluxo e os dados; para validar o HTTP recebido pelo cliente, use o webhook.

## Consulta via webhook — PowerShell

Com o workflow publicado, substitua a chave abaixo e execute:

```powershell
$apiKey = 'COLE_SUA_CHAVE_AQUI'

curl.exe --include --max-time 30 `
    --get 'https://bot.rsa.ia.br/webhook/wf12-processed-results' `
    --data-urlencode 'source=stackoverflow' `
    --data-urlencode 'tag=artificialintelligence' `
    --header "communitylab-api-key: $apiKey"
```

O comando requisita `processed/result_stackoverflow_artificialintelligence.json` e exibe os headers HTTP e o conteúdo JSON no terminal. `--data-urlencode` preserva caracteres como `+` e `#` nos parâmetros.

Para testar pelo endpoint temporário, troque `/webhook/` por `/webhook-test/` e ative **Listen for test event** no nó Webhook antes da chamada. O endpoint publicado não exige escuta manual. Após alterações no editor, publique novamente para atualizar a versão de produção.

## Parâmetros e resposta

| Parâmetro | Regra |
| --- | --- |
| `source` | Obrigatório: `stackoverflow`, `mastodon` ou `hackernews` |
| `tag` | Obrigatório: tópico exato no nome do arquivo, sem normalização automática; de 1 a 200 caracteres, começando com letra ou número e contendo apenas letras ASCII, números, `.`, `+`, `#`, `_`, `;` ou `-` |

Valores atuais de `tag`: `artificialintelligence`, `docker`.

Resposta de sucesso (exemplo com um registro):

```json
{
  "success": true,
  "statusCode": 200,
  "source": "stackoverflow",
  "tag": "artificialintelligence",
  "object_key": "processed/result_stackoverflow_artificialintelligence.json",
  "count": 1,
  "items": [{ "source_id": "79857625" }]
}
```

Os registros reais são retornados completos, sem alteração dos campos internos. `count` conta os elementos do array principal, não as respostas dentro de `answers`. O formato interno varia conforme a fonte.

| HTTP | Significado |
| --- | --- |
| 200 | Arquivo consultado; array vazio retorna `count: 0` e `items: []` |
| 400 | Parâmetros inválidos (`INVALID_QUERY`) |
| 404 | Arquivo não encontrado (`PROCESSED_FILE_NOT_FOUND`) |
| 502 | Falha de download (`STORAGE_DOWNLOAD_FAILED`) ou extração/formato inválido (`INVALID_PROCESSED_DATA`) |

Para testar a validação, use `source=reddit`. Para testar arquivo inexistente, use `source=stackoverflow` e `tag=teste-arquivo-inexistente-wf12`. A identificação do 404 depende da mensagem textual retornada pelo nó S3.

## Consumo no Streamlit e estado dos testes

O Python do Streamlit deve chamar o endpoint com o header de autenticação, tratar timeout e erros HTTP e consumir o array `items`. Guarde a chave nos secrets da aplicação. O WF12 fornece o endpoint; a integração da interface ainda precisa ser implementada.

Foram confirmados HTTP 200, 400 e 404 via webhook. Nos testes manuais de Stack Overflow, os tópicos `artificialintelligence` e `docker` retornaram 5 e 72 registros, respectivamente. Esses totais podem mudar quando os arquivos forem atualizados.

Permanecem pendentes os testes de JSON malformado, JSON que não seja array, array vazio e consultas válidas de Mastodon e Hacker News. Não versione a chave real de API.
