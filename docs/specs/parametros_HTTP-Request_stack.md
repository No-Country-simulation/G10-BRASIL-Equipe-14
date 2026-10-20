# Consulta a Stack Exchange

Mapeamento dos parâmetros para que o workflow `WF02 - Coleta Stack Exchange` possa atender a diferentes demandas do projeto de acordo com o **endpoint da API**.

A consulta de perguntas, por exemplo, aceita parâmetros diferentes dos endpoints de respostas, usuários, comentários e tags.

## 1. Parâmetros úteis para consultar perguntas

O endpoint utilizado no teste inicial: `GET https://api.stackexchange.com/2.3/questions`

Parâmetro | Função	| Exemplo de valor |
| --- | --- | --- |
| site	| Define o site da rede Stack Exchange	| `stackoverflow`, `superuser`, `askubuntu` |
| pagesize	| Quantidade de registros por página	| `3`, `20`, `100` |
| page	| Número da página consultada	| `1`, `2`, `3` |
| order	| Ordenação crescente ou decrescente	| `asc`, `desc` |
| sort	| Campo usado para ordenar	| `activity`, `creation`, `votes`, `hot`, `week`, `month` |
| fromdate	| Data inicial, em Unix timestamp	| `1792454400` |
| todate	| Data final, em Unix timestamp	| `1792540800` |
| min	| Limite inferior para o campo de ordenação	| Depende de `sort` |
| max	| Limite superior para o campo de ordenação	| Depende de `sort` |
| tagged	| Restringe a consulta por tags	| `python;machine-learning` |
| nottagged	| Exclui perguntas com determinadas tags	| `homework`, `beginner` |
| intitle	| Busca palavras no título	| `data pipeline` |
| `sort` + `min`/`max`	| Permite filtrar por critérios relacionados à ordenação	| `sort=votes`, `min=5` |
| filter	| Define quais campos a resposta da API deve conter	| Filtro predefinido ou personalizado |
| key	| Identifica uma aplicação e pode ampliar a cota disponível	| Chave de API, se necessária |

**Observações:**

* `site` é fundamental: a API consulta um site por requisição. Para pesquisar vários sites, o workflow deverá iterar sobre uma lista de sites.
* `pagesize` pode chegar a 100 nas consultas compatíveis, mas convém começar com valores pequenos para testar o processamento.
* `fromdate` e `todate` permitem limitar a janela temporal; são especialmente úteis para coletas periódicas.
* `tagged` e `nottagged` usam tags, normalmente separadas por ponto e vírgula.
* `filter` é útil para reduzir o volume de dados transferidos, mas precisa ser configurado de acordo com os campos necessários.
* `min` e `max` dependem do campo de ordenação selecionado; não são filtros universais para qualquer atributo.

## 2. Endpoints oficiais

_Endpoints_ que podem ser úteis para o projeto.

| Tipo de dado	| Endpoint	| Parâmetros específicos úteis	| Aplicação no projeto |
| --- | --- | --- | --- |
| Busca textual de perguntas	| `/2.3/search` |	`intitle`, `tagged`, `nottagged`	| Encontrar discussões sobre um tema ou tecnologia |
| Busca avançada	| `/2.3/search/advanced`	| `q`, `title`, `body`, `tagged`, `nottagged`, `accepted`, `answers`, `views`, `user`, `url`, `closed`, `wiki`	| Pesquisar perguntas com critérios mais específicos |
| Perguntas sem respostas	| `/2.3/questions/no-answers`	| `tagged`, `fromdate`, `todate`, `sort`	| Identificar problemas ainda sem resposta |
| Perguntas não respondidas satisfatoriamente	| `/2.3/questions/unanswered`	| `tagged`, `fromdate`, `todate`, `sort`	| Identificar dúvidas que continuam sem solução aceita ou suficiente |
| Respostas	| /2.3/questions/{ids}/answers	| IDs das perguntas, `sort`, `order`, datas e paginação, conforme o método	| Coletar soluções propostas para perguntas selecionadas |
| Usuários	| `/2.3/users`	| `inname`, `sort`, `min`, `max`, datas	| Consultar perfis públicos e dados de reputação |
| Tags	| `/2.3/tags`	| `inname`, `sort`, `order`, paginação	| Descobrir tags e medir sua popularidade |
| Comentários	| `/2.3/comments`	| `sort`, `min`, `max`, `fromdate`, `todate`	| Analisar comentários públicos em um site |
| Publicações — perguntas e respostas	| `/2.3/posts`	| `sort`, `order`, `datas`, `paginação`	| Coletar publicações de forma mais abrangente |

**Observações:**

* Em `/questions`, `tagged=python;machine-learning` exige que a pergunta tenha ambas as tags. Em `/search`, `tagged` funciona como alternativa: a pergunta pode conter pelo menos uma das tags.
* `intitle` e `nottagged` são parâmetros de busca, não parâmetros gerais de `/questions`. Para busca avançada, utlizar `/search/advanced` quando precisar combinar diversos critérios.

A disponibilidade e a interpretação dos parâmetros dependem do endpoint. Seguem referências:
* [Perguntas](https://api.stackexchange.com/docs/questions?utm_source=chatgpt.com)
* [Busca](https://api.stackexchange.com/docs/search?utm_source=chatgpt.com)
* [Busca avançada](https://api.stackexchange.com/docs/advanced-search?utm_source=chatgpt.com)
* [Respostas](https://api.stackexchange.com/docs/answers?utm_source=chatgpt.com)
* [Tags](https://api.stackexchange.com/docs/tags?utm_source=chatgpt.com)


## 3. Parâmetros comuns que vale mapear no n8n

Além dos parâmetros da API, o próprio nó `HTTP Request` tem configurações que afetam como a coleta funciona. A coluna _Recomendação_ mostra o que é útil para início do projeto, sendo possível alterar conforme demanda.

| Configuração do nó	| Para que serve	| Recomendação |
| --- | --- | --- |
| Method	| Método HTTP	| `GET` para consultas públicas |
| URL	| Endpoint chamado	| Definido conforme o tipo de dado |
| Authentication	Autenticação da requisição	| `None` para os testes públicos atuais |
| Send Query Parameters	| Envia filtros na URL	| Ativado |
| Query Parameters	| Lista de parâmetros e valores	| Configurável conforme cada coleta |
| Send Headers	| Envia cabeçalhos HTTP	| Deixar desativado até existir necessidade |
| Send Body	| Envia corpo da requisição	| Não necessário para consultas GET |
| Response Format	| Formato esperado da resposta	| JSON |
| Pagination	| Permite buscar páginas adicionais	| Configurar quando for necessário coletar mais de uma página |
| Timeout	| Tempo máximo de espera	| Definir de acordo com a duração esperada da consulta |
| Retry on Fail	| Tenta novamente em caso de falha	| Avaliar quando o workflow estiver mais estável |

A API usa paginação: `page` começa em 1 e `pagesize` pode chegar a 100. A resposta inclui `has_more`, que indica se existem mais resultados. Para coleta completa, o workflow deve considerar esse campo e respeitar os limites de requisição.

A consulta total pode ser feita definindo `filter=total`, obtendo dados do Stack Exchange de um ano.
URL de consulta com essa definição: `https://api.stackexchange.com/2.3/questions?site=stackoverflow&tagged=artificial-intelligence&fromdate=1729445640&filter=total`

Existem outros parâmetros dentro desse nó, conforme pode ser visto na [Documentação oficial](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest), que também podem ser explorados conforme demanda. 


## 4. Parâmetros de controle e qualidade dos dados

Estes campos da resposta podem ser considerados pelo workflow, pois ajudam a controlar a coleta.

| Campo retornado	| Significado	| Uso no projeto |
| --- | --- | --- |
| `items`	| Registros coletados	| Fonte dos dados que serão tratados |
| `has_more`	| Indica se existem mais páginas	| Controlar a paginação |
| `quota_remaining`	| Cota restante informada pela API	| Monitorar consumo |
| `quota_max`	| Cota máxima informada na resposta |	Acompanhar limites |
| `backoff`	| Tempo de espera solicitado pela API, quando presente	| Aguardar antes de fazer novas chamadas ao método afetado |
| `error_id`, `error_message`	| Informações de erro, quando presentes |	Diagnosticar falhas |
| `total` |	Quantidade total de resultados, quando solicitada por um filtro apropriado	| Estatísticas e estimativas de volume |

Esses campos pertencem ao objeto de resposta comum da API. O campo `backoff` merece atenção especial: quando retornado, deve ser respeitado antes de repetir chamadas ao método afetado.