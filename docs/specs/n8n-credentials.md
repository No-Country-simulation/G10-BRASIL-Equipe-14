# Credenciais n8n

Os workflows utilizados para **Stack Overflow** utilizam credencial do tipo **Header Auth**, com o cabeçalho `communitylab-api-key`:

| Credencial | Allowed HTTP Request Domains | Workflows |
|---|---|---|
| `Hackathon CommunityLab` | `None` | WF02, WF03, WF04, WF05 |

O workflow WF06, referente ao Mastodon, ainda está em desenvolvimento.

O workflow WF07, referente ao **Hacker News** não requer autenticação. 

Ação de cada workflow:

Webhook URL: `https://bot.rsa.ia.br/webhook/PATH`

| Workflow | PATH | Dado coletado | Fonte |
|---|---|---| --- |
WF02 | `wf02-coleta-stack-exchange` | Questões | Stack Exchange |
WF03 | `wf03-coleta-stack-exchange-licenses` | Licenças | Stack Exchange |
WF04 | `wf04-coleta-stack-exchange-answers` | Respostas | Stack Exchange |
WF05 | `wf05-download-bucket-OCI` | Download dos arquivos em `.ZIP` | Bucket na OCI |
WF06 | `wf06-coleta-mastodon` | Dados | Mastodon |
WF07 | `wf07-hacker-news-search` | Dados completos | Hacker News |
WF08 | `wf08_merge-stackexchange-data` | Questões, licenças, respostas combinadas | Stack Exchange |
WF09 | `wf09_triagem-llm-router-mastodon` | Avaliação de publicações | Mastodon |
WF10 | `wf10_triagem-llm-router_stackexchange` | Avaliação de perguntas e respostas | Stack Exchange |

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