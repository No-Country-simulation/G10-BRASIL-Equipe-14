# Requisições Powershell para os Workflows de triagem

## Requisição para WF09

Triagem das publicações do Mastodon.

```powershell
$webhookUrl = "https://bot.rsa.ia.br/webhook/wf09_triagem-llm-router-mastodon"

$headers = @{
    "Content-Type" = "application/json"
    "communitylab-api-key" = "SUA_CHAVE"
}

$body = @{
    source = "mastodon"
    message = "Teste de invocação do workflow WF08."
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod `
    -Uri $webhookUrl `
    -Method POST `
    -Headers $headers `
    -Body $body

$response | ConvertTo-Json -Depth 20
```


## Requisição para WF10

Triagem de cada resposta aos questionamentos publicados no `source`.

```powershell
$webhookUrl = "https://bot.rsa.ia.br/webhook/wf10_triagem-llm-router_stackoverflow"

$headers = @{
    "Content-Type" = "application/json"
    "communitylab-api-key" = "SUA_CHAVE"
}

$body = @{
    source = "stackoverflow"
    file_type = ".json"
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod `
    -Uri $webhookUrl `
    -Method POST `
    -Headers $headers `
    -Body $body

$response | ConvertTo-Json -Depth 20
```