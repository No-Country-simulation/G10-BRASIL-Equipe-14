# Integração do OCI Object Storage com n8n

- **Projeto:** CommunityLab - Motor Inteligente
de Transformação e Distribuição para Comunidades Digitais
- **Responsáveis:** Equipe 14 - Turma G10
- **Status:** Aprovado / Em Implementação
- **Versão:** 1.0 (Semana 1)
- **Última Atualização:** 19 de Outubro de 2026

---

## Sumário

- [1. Objetivo](#1-objetivo)
- [2. Infraestrutura](#2-infraestrutura)
- [3. Workflow n8n](#3-workflow-n8n)
    - [3.1. Fluxo de Processamento ](#31-fluxo-de-processamento)
    - [3.2. Endpoint de Teste](#32-endpoint-de-teste)
    - [3.3. Destino do Objeto](#33-destino-do-objeto)
- [4. Configuração das Credenciais](#4-configuração-das-credenciais)
- [5. Evidências de Validação](#5-evidências-de-validação)
- [6. Segurança e Limitações](#6-segurança-e-limitações)
- [7. Próximas Etapas](#7-próximas-etapas)

---

## 1. Objetivo

Documentar a integração entre o n8n e o Oracle Cloud Infrastructure (OCI) Object Storage para o projeto CommunityLab, incluindo a infraestrutura utilizada, o workflow de ingestão, os requisitos de configuração, as evidências de validação e os cuidados de segurança.

## 2. Infraestrutura

- **Provedor:** Oracle Cloud Infrastructure (OCI)
- **Região:** `sa-saopaulo-1`
- **Namespace:** `grue2tm7tuaq`
- **Bucket:** `communitylab-assets`
- **Política de acesso:** privado
- **Camada de armazenamento:** Standard
- **Integração:** API compatível com S3

O bucket é privado e exige credenciais válidas e permissões apropriadas para acessar os objetos.

## 3. Workflow n8n

O workflow reutilizável está disponível em:

`n8n/workflows/communitylab-oci-object-storage-ingestion.json`

### 3.1. Fluxo de processamento

O workflow contém os seguintes nós:

1. **Webhook Receptor:** recebe requisições HTTP do tipo `POST`.
2. **Processa Payload:** prepara o JSON recebido, registra os nomes dos campos e adiciona a data e hora de recebimento.
3. **Convert to File:** converte os dados processados em um arquivo JSON binário.
4. **Upload a file:** envia o arquivo ao OCI Object Storage por meio da API compatível com S3.
5. **Resposta de Sucesso:** retorna uma resposta JSON HTTP 200 após a execução bem-sucedida do nó de upload.

### 3.2. Endpoint de teste

- **Método HTTP:** `POST`
- **Caminho:** `/webhook-test/test-ingestion`
- **Formato do payload:** JSON

O caminho `/webhook-test/` é utilizado durante testes manuais no n8n. A URL e o procedimento de ativação do webhook de produção dependem da instância utilizada.

### 3.3. Destino do objeto

O workflow grava o arquivo no seguinte caminho dentro do bucket:

`tests/communitylab-ingestion-test.json`

O nome do objeto está fixo na configuração atual. Portanto, execuções sucessivas podem substituir o arquivo anteriormente armazenado.

## 4. Configuração das credenciais

A exportação do workflow não deve conter chaves secretas nem outros dados de autenticação.

Antes de executar o workflow em outra instância do n8n, é necessário configurar uma credencial compatível com S3 contendo os seguintes parâmetros:

- **Endpoint:** `https://grue2tm7tuaq.compat.objectstorage.sa-saopaulo-1.oraclecloud.com`
- **Região:** `sa-saopaulo-1`
- **Force Path Style:** habilitado
- **Ignore SSL Issues:** desabilitado
- **Access Key ID e Secret Access Key:** configurados de forma segura a partir de uma identidade OCI autorizada.

A identidade utilizada precisa ter permissão para gravar objetos no bucket de destino. Operações adicionais, como listar ou baixar objetos, podem exigir permissões específicas.

Cada integrante deve utilizar credenciais autorizadas para seu próprio acesso. Não devem ser compartilhadas chaves pessoais nem adicionados arquivos de credenciais ao repositório.

## 5. Evidências de validação

O teste inicial foi executado no Windows por meio do comando `curl.exe`:

```powershell
curl.exe -X POST "https://bot.rsa.ia.br/webhook-test/test-ingestion" -H "Content-Type: application/json" -d "{\"nome\":\"Teste CommunityLab\",\"origem\":\"CMD Windows\",\"valor\":123}"
```

### Resultados observados

- A requisição retornou `{"success":true}`.
- Os cinco nós do workflow foram executados com sucesso.
- O objeto armazenado foi baixado pelo Console da OCI.
- O conteúdo do JSON baixado preservou os campos originais `nome`, `origem` e `valor` dentro do payload processado.

Esses resultados validam o envio e a recuperação do objeto no ambiente utilizado no teste inicial.

**Limitação:** a reprodução do teste por outros integrantes da equipe ainda não foi validada.

## 6. Segurança e limitações

- Manter o bucket privado.

- Não versionar Access Key IDs associados a credenciais privadas quando não forem necessários, Secret Access Keys, tokens, senhas ou exportações de credenciais.

- Não compartilhar chaves pessoais da OCI entre integrantes.

- Configurar as credenciais separadamente em cada instância do n8n, conforme as permissões concedidas.

- Respeitar as cotas e condições aplicáveis ao OCI Always Free.
- Não utilizar dados sensíveis nos payloads de teste.

- Considerar que o caminho do objeto está fixo e que execuções concorrentes podem sobrescrever o mesmo arquivo.

- Reconhecer que o workflow atual realiza a ingestão e o armazenamento de objetos, mas não implementa um endpoint geral de download autenticado.

## 7. Próximas etapas

Em uma tarefa posterior, definir e validar um mecanismo autorizado para que os integrantes do CommunityLab possam enviar e recuperar objetos do bucket.

Essa solução deverá contemplar autenticação, autorização, controle de acesso aos objetos e registro das operações realizadas.
