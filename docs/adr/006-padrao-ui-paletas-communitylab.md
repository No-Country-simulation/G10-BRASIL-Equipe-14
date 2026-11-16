# ADR 006 — Padrão visual, paletas e responsividade

Data: 16/11/2026

Status: adotado. A separação de paletas de sentimentos e estados operacionais é provisória, sujeita a revisão após alinhamento da equipe.

## Referência e decisão

O padrão oficial passa a ser o [Guia de Normatização UI/UX do Michael](../specs/guia_de_normatiza_o_ui_communitylab.md). A [especificação anterior](../specs/estrutura_identidade_design.md) complementa somente o comportamento responsivo não detalhado pelo guia. Permanecem as decisões do projeto sobre tema exclusivamente claro, menu sem grupos recolhíveis e atualização explícita do treemap.

As cores, fonte e paletas são centralizadas em `src/design.py`. Configurações nativas em `.streamlit/config.toml` e `.setup/docker/streamlit/config.toml` usam o mesmo tema; a seção de servidor do Docker é preservada.

## Separação entre categorias e estados

Sentimento descreve emoção e não deve representar sucesso de processamento, aprovação, alerta ou falha. Em particular, “Irritado” não significa erro operacional, e “Neutro” não significa sucesso.

As combinações pastel/texto do guia são mantidas para sentimentos, sem os rótulos operacionais associados no documento original:

| Sentimento | Fundo | Texto |
| --- | --- | --- |
| Entusiasmado | `#E2D9EE` | `#4B326B` |
| Satisfeito | `#F4E3C9` | `#7C5318` |
| Neutro | `#D8E6D6` | `#2D5A36` |
| Decepcionado | `#D6E2EE` | `#294A6B` |
| Irritado | `#D1EAE5` | `#1B5E52` |

Estados operacionais usam tokens próprios: sucesso (verde), informação (azul), atenção (âmbar) e erro (vermelho). Badges de aprovação/rejeição e estado do pacote usam esses tokens, sem inferir o estado a partir do sentimento.

Essa separação deve ser revisada nesta ADR e nos tokens após a decisão da equipe, sem alterar as classificações armazenadas nos dados.

## Paletas fixas por categoria

Cada par categoria/valor tem uma associação explícita que não depende da posição na hierarquia ou dos valores presentes no recorte:

- **Fonte:** Mastodon em lilás, Hacker News em areia e Stack Overflow em azul.
- **Tema:** inteligência artificial em lilás; Docker em azul; interfaces em verde-água; sistemas em verde; DevOps em cinza; desenvolvimento móvel em areia; aprendizado de máquina em rosa suave; carreira em oliva suave.
- **Editorial:** caso de sucesso em verde; FAQ em azul; newsletter em lilás; moderação em areia; descarte em cinza; outro em oliva; encaminhamento alternativo em verde-água; sem classificação em cinza.
- **Sentimento:** tabela acima; sem avaliação em cinza.

As cinco cores pastel do Michael são a base. Cinza estrutural e variações suaves rosa/oliva completam as categorias com mais valores. Valores desconhecidos recebem uma cor calculada por hash determinístico de categoria/valor, sem remapear os demais. Cores podem ser reutilizadas entre categorias e não são identificadores exclusivos; o caminho, os rótulos e a hierarquia distinguem os grupos.

No treemap, cada nó usa a cor do seu próprio nível, inclusive ao reordenar ou ocultar categorias. Os textos dos blocos permanecem escuros para contraste uniforme, com detalhes no texto de apoio. As cores não alteram contagens, filtros ou decisões editoriais.

## Tipografia e contraste

Botões primários e kicker usam `#157A56`, com hover `#106144`. O esmeralda `#1AA878` não é utilizado em textos pequenos. Títulos/KPIs usam `#0F172A`; texto secundário `#475569`; metadados `#64748B`.

Família declarada: `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`. Nenhuma fonte é baixada. O navegador escolhe a primeira disponível: no Windows, normalmente Segoe UI quando Inter não estiver instalada; em outros dispositivos, a fonte de sistema correspondente. A mesma sequência é aplicada aos gráficos.

## Comportamento responsivo

A especificação anterior pede conteúdo fluido, menu recolhível, adaptação ao tamanho da tela e margens de referência de 24–32 px, mas não define pontos de quebra. Para concretizar essas diretrizes:

- **Acima de 1100 px:** quatro KPIs em linha; sidebar de 260 px; área principal limitada a 1720 px.
- **De 769 a 1100 px:** KPIs em duas colunas e margens laterais de 24 px.
- **Até 768 px:** KPIs empilhados, margens de 16 px, título de 24 px, barra superior com quebra de linha e controles do treemap com redistribuição de linhas.
- O menu conserva o controle nativo de recolhimento do Streamlit. Em telas estreitas, o comportamento nativo permite liberar a área principal.
- O espaço superior permanece reservado para o cabeçalho fixo do Streamlit, evitando o corte dos títulos. Tabelas mantêm rolagem horizontal própria.
- O rodapé da sidebar é empurrado para a base quando houver espaço; continua no fluxo se o conteúdo exceder a tela, evitando sobreposição.

Os pontos de quebra são decisões desta implementação, e não números prescritos no documento anterior.

## Idioma e manutenção

Textos produzidos pela aplicação, placeholders, rótulos e orientações ficam em português brasileiro. Nomes próprios, siglas, identificadores de contratos e conteúdo original das publicações são preservados.

`src/ui_localization.py` traduz textos fixos de controles nativos que não têm configuração de idioma pela API Python instalada. O adaptador usa código estático e seletores de componentes, sem interpolar conteúdo do usuário e sem traduzir os dados. Deve ser revisto com atualizações do Streamlit; textos internos novos de componentes de terceiros podem exigir ampliação do mapeamento. A tradução não muda a lógica dos controles.

## Validação

Testes verificam as cores por categoria nas diferentes ordens do treemap, a estabilidade sob filtros, o contraste dos pares de texto/fundo, a equivalência entre temas local/Docker e os fluxos existentes. Inspeção visual em navegador continua necessária para homologar dimensões, tradução de controles internos e comportamento responsivo.
