# Declaração de deploy na OCI — S4-01

Em **20/11/2026, no horário de São Paulo**, o CommunityLab foi publicado na OCI com acesso restrito à equipe em [communitylab.rsa.ia.br](https://communitylab.rsa.ia.br/). Este registro complementa a [homologação funcional da S4-01](homologacao-S4-01.md) da [issue #24](https://github.com/No-Country-simulation/G10-BRASIL-Equipe-14/issues/24).

## Revisão e ambiente

| Item | Configuração |
|---|---|
| Código implantado | Commit `4b70a3a4fce8` da branch `docs/S4-06-data-dictionary-execution-flow` |
| Imagem local | `communitylab-streamlit:4b70a3a4fce8` (`linux/arm64`) |
| ID da imagem | `sha256:2b9554d0adb5eab87f6ea1545faa1f7079e3681a0b00a9dc644c489dd08d535b` |
| Instância OCI | `VM.Standard.A1.Flex` em `sa-saopaulo-1`, com Ubuntu 24.04 LTS, 2 OCPUs e 12 GB de RAM |
| Serviços | Streamlit no projeto Compose `communitylab-homolog`. Caddy e n8n no projeto existente `n8n-stack` |
| Entrada HTTPS | Subdomínio apontado para a instância, com autenticação HTTP Basic no Caddy. Porta `8501` vinculada ao loopback da VM |
| Rede do proxy | Rede Docker interna `communitylab-proxy`, declarada como externa nos dois projetos Compose. O Caddy encaminha para `communitylab-upstream:8501` |
| Dados | Bucket `communitylab-assets` e diretórios locais persistentes `data/` e `aprovados/` |

## Evidências de aceite do deploy

| Verificação | Resultado observado |
|---|---|
| Acesso ao painel | Acesso inicial por túnel SSH e acesso posterior por HTTPS. Sem credenciais, o Caddy respondeu `HTTP 401`. Com as credenciais da equipe, o painel abriu e a tabela respondeu à mudança de fonte |
| Download pelo n8n | O WF05 publicado recebeu a chamada autenticada a partir do contêiner e devolveu um ZIP válido de `processed/`, com 33 arquivos e 385.685 bytes. O download também foi concluído pela tela **Ingestão de dados** |
| Leitura direta do Object Storage | A ação **Dados processados → Atualizar dados** carregou o snapshot do bucket no DuckDB. A tabela exibiu os registros segundo os filtros de fonte e tag |
| Persistência do DuckDB | Após recriar o Streamlit, os dados continuaram disponíveis e o painel manteve a última carga de `21/11/2026 00:13:15 UTC` (`20/11/2026 21:13:15` em São Paulo) |
| Roteamento após recriação | Após remover a conexão temporária do Caddy e recriar o Streamlit, o contêiner voltou `Healthy`. O health check respondeu `ok` pela rede dedicada e pelo HTTPS autenticado. A raiz de `bot.rsa.ia.br` respondeu `HTTP 200` |

## Verificação de manutenção

O Compose do Caddy foi validado com a rede dedicada. A recriação do próprio Caddy ficou para uma janela de manutenção devido à breve interrupção de HTTPS que causaria no n8n.
