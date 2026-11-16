# Interface interna do CommunityLab

A aplicação segue o padrão oficial de `guia_de_normatiza_o_ui_communitylab.md` e o desafio CommunityLab: transformar conversas em inteligência e ativos editoriais com revisão humana. A especificação `estrutura_identidade_design.md` complementa as diretrizes responsivas. As decisões e paletas estão registradas na [ADR 006](../adr/006-padrao-ui-paletas-communitylab.md). O ponto de entrada é `src/main.py`.

## Organização

- **Visão executiva:** indicadores do consolidado, prioridades de revisão em um painel de largura total e atalhos para os próximos passos do fluxo operacional.
- **Sentimentos e tópicos:** filtros, indicadores, treemap das avaliações, pesquisa e exportação do recorte em CSV, além do assistente contextual. O treemap inicia na ordem fonte → tema da coleta → editorial → sentimento, com um checkbox para ativar cada nível e um seletor de posição de 1 a 4 antes de cada categoria. Alterar a posição troca as categorias de lugar, preservando posições únicas; o gráfico segue a ordem dos níveis ativos. O tamanho representa associações únicas entre interação e tema; ocultar ou reordenar níveis preserva o total.
- **Ingestão:** orientações, inclusão de arquivos/texto, validação, prévia e confirmação de envio. Mantém as validações e a integração existentes.
- **Fontes da comunidade:** filtros e lotes demonstrativos, explicitamente identificados. O botão simula o processamento.
- **Curadoria:** seleção de lote, contagem por estado, edição, aprovação/rejeição, reabertura e exportação dos conteúdos aprovados em JSON. Os pacotes são demonstrativos e a revisão dura somente a sessão.

## Identidade e manutenção

`src/design.py` centraliza cores, fontes e paletas fixas por categoria, separadas dos estados operacionais. `src/ui.py` aplica estilos, cabeçalhos, cards, badges e configuração visual dos gráficos Plotly. `.streamlit/config.toml` e a configuração Docker compartilham o tema claro. O logo é carregado de `docs/assets/logo-communitylab.svg`, incluindo o ícone da página. O adaptador `src/ui_localization.py` traduz textos fixos de controles nativos; deve ser conferido nas atualizações do Streamlit.

O botão **Atualizar**, na mesma linha dos controles do treemap, aplica os níveis ativos e suas posições. Alterações nos checkboxes ou seletores ficam pendentes até o clique; a hierarquia exibida corresponde à configuração aplicada. Os filtros de dados continuam atualizando o recorte com a última configuração aplicada.

Use `page_header`, `metric_card`, `badges` e `style_chart` em novas páginas. Conteúdo interpolado nos componentes HTML é escapado. Preserve rótulos dos campos, foco por teclado, o controle nativo de recolhimento da navegação e mensagens textuais de estado. Os estilos usam seletores `data-testid` do Streamlit e devem ser revisados ao atualizar a biblioteca.

O consolidado é consultado sem alterar os dados. A última carga exibida corresponde ao snapshot, no fuso de Brasília. Não se inventam metas ou variações sem referência comparável. A marcação “uso interno” descreve o contexto de uso; autenticação depende da infraestrutura de implantação existente.

## Verificação

Executar com o ambiente do projeto:

```powershell
.venv/Scripts/python.exe -m streamlit run src/main.py
.venv/Scripts/python.exe -m pytest tests/test_workspace_ui.py tests/test_ingestion_view.py tests/test_sentiment_dashboard.py tests/test_sentiment_treemap.py tests/test_sentiment_chat.py -q
```

Os testes de interface percorrem as cinco páginas no tema claro, verificam a ausência do seletor de aparência, o contraste dos tokens de texto e ações e a edição, aprovação e reabertura de um conteúdo. Eles verificam a execução dos componentes, mas não substituem a inspeção visual em navegador nos tamanhos desktop e móvel.
