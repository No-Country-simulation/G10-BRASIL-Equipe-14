# Contrato de API — Stack Exchange

**Projeto:** CommunityLab  
**Base URL:** `https://bot.rsa.ia.br`  
**Versão:** 1.0  
**Formato:** JSON UTF-8 e download de arquivo JSON  
**Autenticação:** Header Auth

## 1. Visão geral

As integrações disponíveis com o n8n estão apresentadas em [n8n-credentials](./n8n-credentials.md).

| Workflow | Arquivo | Dado coletado |
| --- | --- | --- |
WF02 | [wf02](../../n8n/workflows/wf02_coleta-stack-exchange-questions-integrada.json) | Perguntas |
WF03 | [wf03](../../n8n/workflows/wf03_coleta-stack-exchange-licenses-integrada.json) | Licenças | 
WF04 | [wf04](../../n8n/workflows/wf04_coleta-stack-exchange-answer-integrada.json) | Respostas | 
WF05 | [wf05](../../n8n/workflows/wf05_download-bucket-OCI.json) | Arquivo `.zip` da OCI |

Esse arquivo `.zip` recupera todos os arquivos presentes no bucket da OCI. 

## 2. Autenticação

As operações exigem autenticação por cabeçalho HTTP.

* Nome do cabeçalho: `communitylab-api-key`
* Valor: Chave de API fornecida para o consumidor

Exemplo de cabeçalho:

```http
communitylab-api-key: <SUA_CHAVE_DE_API>
```

A chave deve ser armazenada em um mecanismo seguro de gestão de segredos. Não deve ser incluída no código-fonte, no repositório Git ou em logs.

O consumidor deve enviar o cabeçalho nas duas operações, inclusive no download do arquivo.

## 3. Integração com Stack Exchange

### Requisição

**Método:** `POST`

**URL:**

`https://bot.rsa.ia.br/webhook/wf04-integracao-stack-exchange`

**Content-Type:** `application/json`

### Parâmetros de entrada

| Campo | Tipo | Valor padrão | Descrição |
|---|---|---|---|
| `tagged` | _string_ | `artificial-intelligence` | Tag utilizada para filtrar perguntas |
| `fromdate` | _integer_ | `1760929200` | Timestamp Unix que define o início do período de coleta |
| `pagesize` | _integer_ | `100` | Quantidade solicitada por página à API de origem |
| `site` | _string_ | `stackoverflow` | Comunidade do Stack Exchange |

Os valores padrão são os configurados no workflow. Os limites efetivamente aceitos para cada parâmetro devem respeitar as regras da API do Stack Exchange.

#### Valores para o parâmetro `site` no Stack Exchange

Existem 183 sites, ou comunidades, disponíveis no Stack Exchange para requisição. O Stack Overflow é somente um dos sites disponíveis. Na [relação de sites](https://stackexchange.com/sites?view=list#oldest), ordenada por _Oldest_, observa-se a presença do `stackoverflow` como o mais antigo, com mais de 18 anos, 24 milhões de questões, 36 milhões de respostas e 32 milhões de usuários. Os cinco sites com as maiores questões por dia:

| Site | Tópico | Requisições/dia | Idade |
|---|---|---|---|
| `stackoverflow` | Q&A for professional and enthusiast programmers | 59 | 18y3m |
| `math.exchange` | Q&A for people studying math at any level and professionals in related fields | 26 | 16y3m |
| `mathoverflow`| Q&A for professional mathematicians | 12 | 17y1m |
| `askubuntu` | Q&A for Ubuntu users and developers | 11 | 16y3m |
| `physics.stackexchange` | Q&A for active researchers, academics and students of physics | 7,9 | 15y11m |

 **Observação: **Informações obtidas no dia 28/10/2026.


## 4. Tratamento de erros

Os nós `Webhook`, `Respond to webhook` e `HTTP Request` estão com a configuração `Retry on Fail` ativada, com 3 tentativas e intervalo de 3 segundos.

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
