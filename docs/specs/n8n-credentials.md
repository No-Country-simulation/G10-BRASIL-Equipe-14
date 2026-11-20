# Credenciais n8n

Os webhooks abaixo usam a credencial **Header Auth** com o cabeçalho `communitylab-api-key`.

| Credencial | Allowed HTTP Request Domains | Workflows |
|---|---|---|
| `Hackathon CommunityLab` | `None` | WF02–WF13 |

O webhook de coleta do Mastodon (WF06) também usa `Hackathon CommunityLab` no export versionado.

Ação de cada workflow:

Webhook URL: `https://bot.rsa.ia.br/webhook/PATH`

| Workflow | PATH | Dado coletado | Fonte |
|---|---|---| --- |
WF02 | `wf02-coleta-stack-exchange` | Questões | Stack Exchange |
WF03 | `wf03-coleta-stack-exchange-licenses` | Licenças | Stack Exchange |
WF04 | `wf04-coleta-stack-exchange-answers` | Respostas | Stack Exchange |
WF05 | `wf05-download-bucket-OCI` | Download dos arquivos em `.ZIP` |Pasta do bucket OCI definida no parâmetro `folder` do nó `Edit Fieds` |
WF06 | `wf06-coleta-mastodon` | Dados | Mastodon |
WF07 | `wf07-hacker-news-search` | Dados completos | Hacker News |
WF08 | `wf08_merge-stackexchange-data` | Questões, licenças, respostas combinadas | Pasta `raw/` do bucket OCI |
WF09 | `wf09_triagem-llm-router-mastodon` | Avaliação de publicações | Mastodon |
WF10 | `wf10_triagem-llm-router_stackexchange` | Avaliação de perguntas e respostas | Pasta `raw/` do bucket OCI |
WF11 | `wf11_triagem-llm-router_hackernews` | Avaliação de comentários com contexto das publicações | Pasta `raw/` do bucket OCI |
WF12 | `wf12-processed-results` | Consulta de um resultado processado por `source` e `tag` (GET) | Pasta `raw/` do bucket OCI |
WF13 | `wf13-sentimento-chat` | Resposta à pergunta enviada com o contexto do painel (POST) | Streamlit |

Além da autenticação do webhook, o WF12 usa a credencial `OCI Object Storage S3` para ler o bucket. O WF13 usa `NVIDIA Nemotron account` no modelo principal e `OpenRouter - ONE_hackathon` no modelo de fallback. Selecione as credenciais correspondentes nos nós após a importação.

O Streamlit envia `N8N_API_KEY` no cabeçalho `communitylab-api-key` nas chamadas ao WF05 e ao WF13. Para o WF13, `N8N_SENTIMENT_CHAT_WEBHOOK_URL` permite configurar a URL. O [contrato do WF12](./conexao-streamlit-n8n.md) detalha a chamada autenticada ao endpoint.

As requisições powershell dos workflows com Agente de IA podem ser vistas [aqui](./requisicoes_powershell_triagem.md). 

## Ações futuras
* **Versionamento:** Necessário definir critério de versão na geração dos arquivos, nos fluxos WF02, WF03, WF04, WF06 e WF07.

**Sugestão de requisição via Powershell para WF02:**

```powershell
$headers = @{
    'Content-Type' = 'application/json'
    'communitylab-api-key' = '<CHAVE SECRETA>'
}

$body = @{
    tagged   = 'artificial-intelligence'
    fromdate = 1760929200
    pagesize = 100
    site     = 'stackoverflow'
} | ConvertTo-Json

Invoke-WebRequest `
    -Uri "https://bot.rsa.ia.br/webhook/wf02-coleta-stack-exchange" `
    -Method POST `
    -Headers $headers `
    -Body $body `
    -OutFile "$HOME\Downloads\stackexchange-questions.json" `
    -ErrorAction Stop

Write-Host "Download feito com sucesso."
```

**Disponibilização da chave:** o nome do cabeçalho está documentado para facilitar a configuração. O valor da chave de teste será fornecido **em particular aos integrantes autorizados da equipe, pelo Discord**, e não será incluído neste PR, no repositório ou nos arquivos JSON exportados dos workflows.

Após importar os workflows, cada integrante deverá configurar ou selecionar as credenciais correspondentes no próprio ambiente n8n. Para executar chamadas contra os endpoints hospedados em `bot.rsa.ia.br`, deverá utilizar o valor de chave autorizado pelo servidor.
