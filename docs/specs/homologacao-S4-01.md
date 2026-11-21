# Plano de homologação — S4-01

- Issue: #24
- Branch: feat/S4-01-end-to-end-validation
- Status: três cenários homologados em 19/11/2026 (Brasília)
- Data: 17/11/2026

## Relatório de homologação — 19/11/2026

O aceite da [issue #24](https://github.com/No-Country-simulation/G10-BRASIL-Equipe-14/issues/24) foi atendido. Três entradas sintéticas foram enviadas pela interface do Streamlit, processadas pelo n8n com triagem de IA, transformadas em rascunhos e aprovadas na Curadoria. O responsável gravou os pacotes no bucket `communitylab-assets` e baixou os três objetos para conferência.

| Cenário | Execução | Evidência do resultado | Chave no bucket |
|---|---|---|---|
| 1. Dúvida técnica sobre timeout HTTP | [WF10 10623](https://bot.rsa.ia.br/workflow/fPkrXUK7Kre97d89/executions/10623) | Resposta `91000201` encaminhada para FAQ. FAQ e post para LinkedIn aprovados. | `assets/approved/s4-01/wf10-10623/distribution-package.json` |
| 2. Conquista profissional | [WF09 10624](https://bot.rsa.ia.br/workflow/yyCSYXsAjrxShN4N/executions/10624) | Publicação `91000201` encaminhada para `success_case`. Post para LinkedIn e destaque de newsletter aprovados. A revisão corrigiu o espaçamento da citação no post. | `assets/approved/s4-01/wf09-10624/distribution-package.json` |
| 3. Dúvidas recorrentes sobre reenvio de POST | [WF11 10625](https://bot.rsa.ia.br/workflow/J5K2Oz5cc7oJL8z4/executions/10625) | Três registros triados e dois comentários únicos no resumo. FAQ aprovado com a orientação sobre idempotência do comentário `91000302`. Resumo para newsletter aprovado. | `assets/approved/s4-01/wf11-10625/distribution-package.json` |

Os três arquivos baixados passaram na validação de `data/schemas/output_schema.json`. Cada arquivo contém exatamente os dois ativos aprovados do seu lote, com igualdade nos títulos, textos, destinos e potenciais de engajamento. O ID do pacote, o resumo de processamento, o bucket e a chave também foram conferidos. No cenário 3, a proveniência local confirma que o ID `91000301` foi contado uma vez e que `91000302` fornece a orientação técnica. O texto aprovado do FAQ preserva também o primeiro relato como contexto.

O teste comprova a deduplicação dentro do lote. Uma segunda execução real da mesma entrada e a automação integral da rodada permanecem como verificações complementares. Os testes exploratórios documentados abaixo registram o estado de preparação anterior à rodada final.

## Objetivo

Verificar três cenários pela esteira Streamlit → n8n → IA → OCI,
com evidências de processamento, curadoria, persistência e recuperação.

A avaliação complementar contempla rastreabilidade, datas e qualidade
analítica. Publicações reais permanecem internas. Os três cenários planejados
utilizarão dados sintéticos; o teste exploratório do WF09 registrado abaixo
utilizou publicações reais coletadas pelo responsável, sem reproduzir seus
textos integrais neste documento.

## Limitações atuais

- A implementação da S3-06 está no PR #98, pendente de integração.
- A curadoria examinada utiliza dados demonstrativos e decisões em sessão.
- A execução completa depende da confirmação das conexões entre
  ingestão, triagem, geração, curadoria e persistência.

## Componentes e dependências

| Etapa | Arquivo ou workflow | Entrada | Saída | Situação |
|---|---|---|---|---|
| Entrada pela interface | `src/views/ingestion.py` e `src/services/ingestion.py`; função `send_to_ingestion()` | Arquivos ou texto JSON/CSV, validados por registro contra `data/schemas/input_schema.json` | POST síncrono por registro para `N8N_INGESTION_WEBHOOK_URL`, com JSON e `Idempotency-Key` | Mapeamento estático concluído; receptor não identificado na lista de workflows ativos; cliente sem cabeçalho de autenticação; execução integrada não verificada |
| Triagem Mastodon | WF09 remoto, ID `yyCSYXsAjrxShN4N` | POST autenticado com `tag` e `limit`; publicações lidas de arquivo em `raw/` na OCI | Avaliações de sentimento/editoriais, resultado consolidado e arquivos de roteamento na OCI | Parâmetros e processamento verificados na execução 10578; validação de entrada e qualidade analítica pendentes; não recebe diretamente os registros da tela |

### Registro da tarefa — mapeamento da entrada

- **Data:** 17/11/2026.
- **Situação:** leitura e mapeamento concluídos; conexão com o receptor pendente de definição.
- **Escopo:** inspeção de `src/views/ingestion.py`, `src/services/ingestion.py` e `src/config.py`, complementada pela configuração e pela relação de workflows ativos informadas pelo responsável pelo ambiente.
- **Procedimento:** avaliação estática; nenhuma requisição HTTP, execução de workflow ou gravação na OCI foi realizada nesta tarefa.

#### Comportamento identificado

1. A tela recebe múltiplos arquivos JSON/CSV e/ou texto colado.
2. A ação **Pré-visualizar** interpreta e valida os registros contra o contrato de entrada. Erros impedem a disponibilização da prévia para envio.
3. Alterações na entrada invalidam a prévia anterior por comparação de assinatura.
4. Após **Enviar dados** e **Confirmar envio**, `send_items()` chama `send_to_ingestion()` uma vez por registro, sequencialmente.
5. O serviço faz POST com o registro no corpo JSON, cabeçalho `Idempotency-Key` e timeout configurável.
6. A tela considera respostas HTTP 2xx como sucesso de envio, sem validar o corpo da resposta para comprovar triagem, geração ou persistência.

A assinatura da prévia e o bloqueio de reenvio ficam na sessão do Streamlit; não comprovam persistência ou idempotência no servidor. Em envio parcial, uma nova tentativa percorre novamente todos os registros.

#### Destino e autenticação

- **URL configurada, conforme informação do responsável:** `https://bot.rsa.ia.br/webhook/ingestion`.
- **Regra de configuração:** `N8N_INGESTION_WEBHOOK_URL` explícita tem precedência sobre a combinação `N8N_BASE_URL` + `N8N_INGESTION_WEBHOOK_PATH`.
- **Receptor:** não identificado. Nenhum endpoint da relação abaixo corresponde a `/webhook/ingestion`. Isso não comprova inexistência do endpoint; sua disponibilidade não foi testada.
- **Autenticação dos workflows listados:** Header Auth, credencial denominada `Hackathon CommunityLab`, conforme informado pelo responsável. O nome da credencial não identifica, por si só, o nome do cabeçalho HTTP.
- **Autenticação no cliente examinado:** `send_to_ingestion()` envia `Idempotency-Key`, mas não inclui cabeçalho de autenticação.
- **Configuração em execução:** a informação do `.env` não foi confrontada nesta tarefa com os valores carregados pelo processo Streamlit/container.

#### Workflows ativos informados

Base das URLs: `https://bot.rsa.ia.br`. Todos foram informados como ativos e vinculados à credencial Header Auth `Hackathon CommunityLab`; o estado remoto não foi consultado nesta tarefa.

| Workflow | Método HTTP | Caminho de produção |
|---|---|---|
| WF02 | POST | `/webhook/wf02-coleta-stack-exchange` |
| WF03 | POST | `/webhook/wf03-coleta-stack-exchange-licenses` |
| WF04 | POST | `/webhook/wf04-coleta-stack-exchange-answers` |
| WF05 | GET | `/webhook/wf05-download-bucket-OCI` |
| WF06 | POST | `/webhook/wf06-coleta-mastodon` |
| WF07 | POST | `/webhook/wf07-hacker-news-search` |
| WF08 | GET | `/webhook/wf08_merge-stackexchange-data` |
| WF09 | POST | `/webhook/wf09_triagem-llm-router-mastodon` |
| WF10 | POST | `/webhook/wf10_triagem-llm-router_stackexchange` |
| WF11 | POST | `/webhook/wf11_triagem-llm-router_hackernews` |
| WF12 | GET | `/webhook/wf12-processed-results` |
| WF13 | POST | `/webhook/wf13-sentimento-chat` |

#### Pendências e próxima ação

- Identificar ou definir o receptor da entrada, verificando compatibilidade entre o payload da interface e o contrato do workflow escolhido.
- Confirmar o cabeçalho de autenticação exigido pelo receptor e prever seu envio seguro, sem registrar o valor secreto neste documento.
- Verificar o tratamento de `Idempotency-Key` pelo servidor e o contrato de resposta antes de homologar reenvios e processamento completo.
- **Avaliação do WF09:** concluída e registrada abaixo. Ele processa publicações armazenadas na OCI; não é receptor compatível com o payload de registros individuais enviado pela tela. A URL da interface não foi alterada.

### Registro da tarefa — parametrização e teste exploratório do WF09

- **Data:** 17/11/2026.
- **Workflow:** [wf09_triagem-llm-router_mastodon](https://bot.rsa.ia.br/workflow/yyCSYXsAjrxShN4N).
- **Responsabilidades:** alterações, publicação e chamada PowerShell realizadas pelo responsável pelo ambiente; configuração e execução consultadas pelo assistente em modo de leitura.
- **Escopo:** verificar parâmetros via Webhook, limite, preservação de identificadores/datas, avaliações e retorno dos nós de upload. Não constitui execução de um dos três cenários completos da S4-01.

#### Contrato e alterações realizadas

O Webhook aceita POST em `/webhook/wf09_triagem-llm-router-mastodon` e exige o cabeçalho `communitylab-api-key`. O valor secreto não é registrado.

O fluxo inicial é `Webhook → Define Search Parameters → Get OCI Bucket files → Select sample_ json files → Download a file → Extract from File → Split Out`. As publicações vêm de arquivos do bucket, não do corpo da requisição.

No nó **Define Search Parameters**, `source` permanece `mastodon` e `file_type` permanece `.json`. O campo `tag` utiliza:

```javascript
{{ $('Webhook').isExecuted
  ? ($json.body?.tag ?? '')
  : 'artificial intelligence'
}}
```

O campo numérico `limit` utiliza:

```javascript
{{ $('Webhook').isExecuted
  ? Number($json.body?.limit ?? 50)
  : 50
}}
```

O nó **Limit**, em **Max Items**, referencia:

```javascript
{{ $('Define Search Parameters').first().json.limit }}
```

Os nomes dos campos `source` e `tag` foram corrigidos para valores fixos sem o prefixo `=`. As alterações foram publicadas pelo responsável. O ramo Manual Trigger foi preservado com tema padrão `artificial intelligence` e limite 50; sua execução após a alteração ainda não foi comprovada.

#### Execução 10578

O responsável coletou o tema `flask` via WF06 e depois chamou o WF09 pelo PowerShell com:

```json
{
  "tag": "flask",
  "limit": 5
}
```

| Verificação | Resultado observado |
|---|---|
| Modo e status | `webhook`, `success` |
| Horário de Brasília | 17/11/2026, de 17:21:44.874 a 17:23:14.380 |
| Duração | Aproximadamente 89,5 segundos |
| Parâmetros efetivos | `file_type: .json`, `source: mastodon`, `tag: flask`, `limit: 5` |
| Arquivo de origem | `raw/mastodon_flask.json` |
| Registros retornados | 5 publicações, com cinco IDs distintos e datas preservadas |
| Sentimentos | 2 Happy, 2 Neutral e 1 Disappointed |
| Roteamento | 4 para newsletter e 1 para descarte |
| Resposta | `success: true`, `status: success`, `execution_id: 10578`, `count: 5` |

Os nós de conversão e upload registraram sucesso para os arquivos:

```text
processed/result_mastodon_flask.json
processed/routing/newsletter/result_mastodon_newsletter_flask_10578.json
processed/routing/discard/result_mastodon_discard_flask_10578.json
```

A recuperação posterior e a comparação do conteúdo armazenado não foram executadas nesta tarefa. Os uploads confirmam o retorno bem-sucedido das operações, sem substituir essa verificação. O resultado consolidado usa chave estável; novas execuções podem substituir o objeto acessível por essa chave, conforme a configuração de versionamento do bucket.

#### Ressalvas de qualidade — Flask

1. **Ambiguidade do tema:** dois registros tratam de recipientes para bebidas, não do framework Flask. Um foi corretamente encaminhado para descarte; a pergunta sobre recipiente foi classificada como `technical_question` e encaminhada para newsletter. Falta uma regra consistente de aderência ao domínio técnico.
2. **Fidelidade do resumo:** no registro `117551915156671008`, o resumo introduziu uma comparação de desempenho diferente da afirmada no conteúdo analisado. A interpretação requer correção/revisão humana antes de uso como inteligência.
3. **Limpeza textual:** foram observadas palavras concatenadas e resíduos de marcação. A extração HTML precisa preservar separações entre elementos.
4. **Exibição PowerShell:** `editorial=` no formato resumido não indica ausência de dados. A execução contém o objeto editorial completo nos cinco itens.
5. **Escopo analítico:** a contagem de cinco itens inclui conteúdo fora do domínio. Não apresentar essa distribuição como sentimento exclusivamente sobre o framework Flask.

#### Execução 10582 — OCI

Após nova coleta via WF06, o responsável chamou o WF09 com `tag: oci` e `limit: 5`. A execução foi consultada diretamente no n8n, sem repetição da chamada pelo assistente.

| Verificação | Resultado observado |
|---|---|
| Execução, modo e status | `10582`, `webhook`, `success` |
| Horário de Brasília | 17/11/2026, de 17:51:57.537 a 17:53:17.520 |
| Duração | Aproximadamente 80 segundos |
| Parâmetros efetivos | `file_type: .json`, `source: mastodon`, `tag: oci`, `limit: 5` |
| Arquivo de origem | `raw/mastodon_oci.json` |
| Registros avaliados | 5 publicações, com cinco IDs distintos e datas preservadas |
| Sentimentos | 5 Neutral |
| Roteamento | 1 success_case, 2 newsletter_only e 2 discard |
| Resultado consolidado | Upload reportado com sucesso para `processed/result_mastodon_oci.json` |
| Uploads de roteamento | Nós de success_case, newsletter e discard reportaram sucesso |

A recuperação dos objetos e a comparação do conteúdo armazenado permanecem pendentes. A mudança do termo de busca não constitui correção de regra do workflow nem comprova ausência de ambiguidade.

##### Ressalvas de qualidade — OCI

| Registro | Observação e impacto |
|---|---|
| `117631211169776135` | Conteúdo sobre APEXlang e Autonomous Database, aderente ao ecossistema Oracle, classificado como `job_achievement` e `success_case` sem evidência explícita de conquista profissional. A conta é identificada como bot/RSS; não atribuir automaticamente a realização ao distribuidor. |
| `117577674407039530` | Conteúdo sobre contêineres OCI no FreeBSD, sem evidência de relação com Oracle Cloud Infrastructure. O resumo também associa o tutorial ao conjunto de ferramentas citado, exigindo revisão de fidelidade. |
| `117574968721101197` | Conteúdo sobre OCI Database Services e MCP. Resumo e justificativa retornaram em japonês; definir e verificar português como idioma de entrega das análises. |
| `117572293648871860` e `117572279006325980` | Textos após a limpeza predominantemente compostos por hashtags; ambos descartados como ruído. Comparar com a origem antes de concluir se a ausência de conteúdo substantivo é original ou consequência da extração. |

Os cinco sentimentos neutros descrevem o conjunto selecionado, que mistura domínios e textos pouco informativos. Não apresentar essa distribuição como medida exclusiva de sentimento sobre Oracle Cloud Infrastructure.

#### Síntese dos testes exploratórios

| Tema | Execução | Integração técnica | Qualidade analítica |
|---|---|---|---|
| `flask` | 10578 | Parâmetros, cinco resultados, datas e uploads verificados nos registros da execução | Ambiguidade de domínio, limpeza e fidelidade pendentes |
| `oci` | 10582 | Parâmetros, cinco resultados, datas e uploads verificados nos registros da execução | Ambiguidade de domínio, classificação, idioma e fidelidade pendentes |
| `oracle cloud infrastructure` | 10584 | Nenhum arquivo aprovado pelo filtro; execução encerrada sem análise, apesar do status técnico success | Não avaliada nesta execução |
| `oracle cloud infrastructure` | 10585 | Arquivo correto selecionado após correção do filtro; cinco avaliações e uploads reportados com sucesso | Maior aderência na amostra; demanda, fidelidade, limpeza e cobertura temporal ainda exigem revisão |

Os testes são mantidos como evidências complementares. Uma amostra mais aderente não invalida os problemas encontrados nas anteriores. Para verificar correções, utilizar também casos controlados com resultado esperado: conteúdo do domínio Oracle, conteúdo de outro significado de OCI e conteúdo insuficiente para decidir.

#### Correção do filtro e teste — Oracle Cloud Infrastructure

**Execução 10584 — falha de seleção:** em 17/11/2026, das 18:01:03.987 às 18:01:04.197 (Brasília), o Webhook recebeu `tag: oracle cloud infrastructure` e `limit: 5`. A listagem retornou `raw/mastodon_oracle cloud infrastructure.json`, mas o filtro usava `tag.replace(' ', '')`, produzindo o sufixo incompatível `oraclecloud infrastructure.json`. Nenhum arquivo passou. O último nó executado foi **Select sample_ json files**; o status técnico `success` não representa processamento pela IA nem upload de resultados.

**Correção aplicada pelo responsável:** substituir a seleção por prefixo/sufixo por uma comparação da chave completa, normalizando caixa e removendo todos os espaços somente na comparação:

Valor esquerdo:

```javascript
{{ $json.Key.toLowerCase().replace(/\s+/g, '') }}
```

Valor direito, com operador **String → is equal to**:

```javascript
{{ (
  'raw/' +
  $('Define Search Parameters').first().json.source +
  '_' +
  $('Define Search Parameters').first().json.tag +
  $('Define Search Parameters').first().json.file_type
).toLowerCase().replace(/\s+/g, '') }}
```

A chave original é preservada para o download. A regra considera equivalentes nomes que diferem apenas por espaços ou caixa; permanece necessário tratar colisões e múltiplos arquivos correspondentes.

**Execução 10585 — verificação da correção:** consultada no n8n sem nova chamada pelo assistente.

| Verificação | Resultado observado |
|---|---|
| Modo e status | `webhook`, `success` |
| Horário de Brasília | 17/11/2026, de 18:06:38.812 a 18:08:12.215 |
| Duração | Aproximadamente 93,4 segundos |
| Parâmetros | `tag: oracle cloud infrastructure`, `limit: 5` |
| Seleção | Exatamente `raw/mastodon_oracle cloud infrastructure.json` |
| Avaliações | 5 registros com IDs distintos e datas preservadas; 4 Neutral e 1 Disappointed |
| Roteamento | 4 newsletter_only e 1 faq |
| Uploads | Nós do consolidado, newsletter e FAQ reportaram sucesso |
| Recuperação | Ainda não executada para comprovar conteúdo dos objetos |

Arquivos de saída identificados:

```text
processed/result_mastodon_oraclecloud infrastructure.json
processed/routing/faq/result_mastodon_faq_oraclecloud infrastructure_10585.json
processed/routing/newsletter/result_mastodon_newsletter_oraclecloud infrastructure_10585.json
```

**Parecer técnico:** correção do filtro comprovada para esta chave com espaços. A saída ainda usa remoção apenas do primeiro espaço; padronizar nomes de arquivo e confirmar compatibilidade com WF12 e carga do DuckDB antes de considerar resolvida a nomenclatura entre componentes.

**Ressalvas analíticas:** a amostra não apresentou a confusão explícita com contêineres observada em `oci`, mas inclui conteúdos de Java e risco financeiro, que não necessariamente representam demandas de infraestrutura. A publicação explicativa sobre certificação foi classificada como pergunta técnica/FAQ, sem comprovar procura por ajuda ou intenção comercial. No registro `117628501244169028`, o resumo deve preservar o caráter de plano atribuído à publicação, sem transformar a afirmação em fato verificado. Permanecem palavras concatenadas e resíduos de marcação. As datas vão de abril de 2025 a novembro de 2026; não tratar os cinco registros como manifestações recentes ou períodos comparáveis.

#### Parecer consolidado e pendências

- **Comprovado nas execuções 10578, 10582 e 10585:** recebimento de tema e limite pelo Webhook, cinco avaliações por execução com IDs/datas preservados, roteamento e retorno de sucesso dos uploads. A execução 10585 também comprova a seleção da chave com espaços após correção.
- **Ainda não comprovado:** Manual Trigger após a alteração, valores padrão com parâmetros omitidos, rejeição de entradas inválidas, idempotência, recuperação dos objetos e integração com Streamlit/DuckDB.
- **Homologação completa pendente:** estas execuções não incluem entrada pela interface, geração de formatos e aprovação humana.
- **Próxima ação imediata:** definir e aplicar uma regra única para o identificador do tema nos nomes de saída e na resposta do WF09, preservando o tema legível e a chave original de entrada. Conferir compatibilidade com WF12 e carga do DuckDB; não renomear objetos históricos nesta etapa.
- **Próxima alteração funcional prevista:** adicionar validação de `tag` e `limit` após **Define Search Parameters**, antes do acesso à OCI. Entradas inválidas devem receber HTTP 400 sem chamar a IA ou gravar resultados. Definir um teto operacional de processamento e registrar que ele é um limite de proteção, distinto do valor solicitado pelo cliente.
- Após validar o contrato, revisar aderência ao domínio, limpeza textual e fidelidade das avaliações; exportar a versão publicada para o repositório antes da conclusão da entrega.

## Matriz preliminar de aceite

Os critérios abaixo orientam os três cenários completos futuros. Os testes parciais do WF09 acima não comprovam seu atendimento integral.

| Verificação | Critério de aprovação | Evidência |
|---|---|---|
| Entrada | Dados aceitos pelo contrato correspondente | Resultado da validação |
| Triagem | Avaliação vinculada ao ID correto | Entrada e saída correlacionadas |
| Datas | Data da unidade analisada preservada e normalizada | Comparação entre origem e resultado |
| Geração | Pelo menos dois formatos distintos por cenário proposto | Conteúdos gerados |
| Fidelidade | Nenhuma conquista, número ou afirmação inventada | Revisão comparativa |
| Curadoria | Edição e decisão preservadas | Versão revisada e registro da decisão |
| Rejeição | Conteúdo rejeitado excluído do pacote final | Comparação dos itens |
| Persistência | Pacote salvo com identificador próprio | Chave do objeto OCI |
| Recuperação | Conteúdo recuperado corresponde ao aprovado | Comparação do JSON |
| Correlação | Entrada, execução e pacote podem ser relacionados | IDs registrados |
