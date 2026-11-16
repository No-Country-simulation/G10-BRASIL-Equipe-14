# Guia de Normatização UI/UX — CommunityLab (Hackathon)

Este documento define o padrão visual, arquitetural e de componentes para todas as telas do projeto **CommunityLab**, garantindo consistência entre os módulos desenvolvidos pela equipe (baseado no padrão Streamlit/Dashboard Analytics limpo).

---

## 1. Identidade Visual e Paleta de Cores

A interface utiliza uma base clara e minimalista com alto contraste tipográfico e acentos em verde-esmeralda (marca) e tons pastel para categorização de dados.

### Cores Principais (Marca & Ação)
* **Verde Principal (Brand / Botões Primários):** `#157A56` (Hover: `#106144`)
* **Verde Esmeralda (Logo / Destaques / Kicker):** `#1AA878`
* **Azul Petróleo Escuro (Texto Principal / Tipografia Logo):** `#1E2E3B`

### Cores de Superfície e Estrutura
* **Fundo da Área Principal (Main Canvas):** `#F8FAFC`
* **Fundo da Barra Lateral (Sidebar) & Cards:** `#FFFFFF`
* **Bordas e Divisores Sutis:** `#E2E8F0`
* **Item Ativo na Sidebar (Background):** `#EBF5F2` (Texto/Ícone: `#157A56`)

### Tipografia e Hierarquia de Texto
* **Família Tipográfica:** `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, `sans-serif`.
* **Texto Primário (Títulos e Valores KPI):** `#0F172A`
* **Texto Secundário (Subtítulos e Labels):** `#475569`
* **Texto Terciário (Metadados, Breadcrumbs, Rodapés):** `#64748B`

### Cores Semânticas (Gráficos, Treemaps e Badges)
Utilizar tons suaves (pastel) com bordas e textos contrastantes para visualização de sentimentos e fontes:
* **Neutro / Sucesso Positivo:** Fundo `#D8E6D6` | Texto `#2D5A36`
* **Satisfeito / Alerta Leve:** Fundo `#F4E3C9` | Texto `#7C5318`
* **Decepcionado / Info:** Fundo `#D6E2EE` | Texto `#294A6B`
* **Entusiasmado / Destaque:** Fundo `#E2D9EE` | Texto `#4B326B`
* **Irritado / Crítico:** Fundo `#D1EAE5` | Texto `#1B5E52`

---

## 2. Estrutura de Layout (Grid e Navegação)

Todas as telas devem obedecer à divisão fixa de **Sidebar à esquerda** + **Área de Conteúdo fluida à direita**.

### A. Barra Lateral (Sidebar - Largura fixa: `260px`)
1. **Cabeçalho da Marca:** Logotipo `CommunityLab` centralizado ou alinhado à esquerda no topo, seguido pelo nome do produto em negrito (`CommunityLab`) e subtítulo (`Inteligência de comunidades`).
2. **Grupos de Navegação:** Divididos por categorias em fonte pequena e discreta (`Principal`, `Análise`, `Operação`).
   * **Principal:** Visão executiva
   * **Análise:** Sentimentos e tópicos
   * **Operação:** Ingestão de dados, Fontes da comunidade, Curadoria editorial
3. **Estado Ativo:** Pílula arredondada (`border-radius: 6px`) com fundo verde muito claro (`#EBF5F2`) e texto em verde escuro (`#157A56`).
4. **Rodapé da Sidebar:** Fixado na base com linha divisória superior e texto: *"Ambiente de trabalho interno · Análise e curadoria"*.

### B. Cabeçalho da Área Principal (Top Bar & Header)
1. **Barra Superior:** Breadcrumb à esquerda (`CommunityLab / [Nome da Tela]`) e tag de ambiente à direita (`Inteligência editorial · Uso interno`).
2. **Bloco de Título da Página:**
   * **Kicker (Categoria):** Texto em caixa alta, negrito, verde (`#157A56`), `11px`, tracking espaçado (ex: `ANÁLISE / INDICADORES`).
   * **Título Principal (`H1`):** `28px`, peso `700` (Bold), cor `#0F172A`.
   * **Subtítulo Descritivo:** `14px`, cor `#475569`, explicando o objetivo da tela em 1 linha.
   * **Barra de Ação Rápida:** Botão secundário (`Recarregar dados`) + metadado de sincronização (`Última carga: DD/MM/AAAA HH:MM (Brasília) · X registros de origem`).

---

## 3. Padrão de Componentes

### 1. Container de Filtros ("Recorte da análise")
* Card branco (`#FFFFFF`), borda `1px solid #E2E8F0`, `border-radius: 8px`, padding `20px`.
* Grid de 3 colunas na primeira linha e 2 colunas na segunda linha (ou responsivo).
* Inputs estilo *Multi-select* com placeholder `Choose options` ou dropdown simples (`Todas`).
* Checkbox opcional na base do card (ex: `Filtrar por data da interação`).

### 2. Cards de KPI (Indicadores Chave)
* Dispostos em linha (Grid de 4 colunas iguais, `gap: 16px`).
* Card branco (`#FFFFFF`), borda `1px solid #E2E8F0`, `border-radius: 8px`, padding `16px 20px`.
* **Estrutura interna:**
  1. Label superior (`12px`, `#475569`).
  2. Valor principal (`26px`, Bold, `#0F172A`).
  3. Micro-descrição inferior (`11px`, `#64748B`).
* *Nota de rodapé abaixo da linha de KPIs:* Texto explicativo de regra de negócio em `12px` cinza.

### 3. Seções de Conteúdo e Visualização
* Títulos de seção em `18px` Bold (`#0F172A`) acompanhados de texto instrutivo logo abaixo.
* **Botões Primários:** Fundo `#157A56`, texto branco, `border-radius: 6px`, ícone à esquerda (ex: `Atualizar`, `Enviar pergunta`).
* **Botões Secundários:** Fundo `#FFFFFF`, borda `1px solid #CBD5E1`, texto `#334155`, `border-radius: 6px` (ex: `Recarregar dados`, `Exportar recorte em CSV`, `Limpar conversa`).

### 4. Tabelas de Dados (Expander / Accordion)
* Encapsulada em um container recolhível (`> Interações e origem dos dados`).
* Possui campo de busca interna (`Pesquisar nas interações`), tabela com cabeçalho fixo cinza claro (`#F8FAFC`), alinhamento à direita para números (`0.90`, `75`) e checkboxes centralizados para status booleanos (`Requer revisão`).
* Botão de exportação CSV no rodapé esquerdo da tabela.

### 5. Assistente de Análise (Chatbot Integrado)
* Seção dedicada na base da tela (ou drawer) com título `Assistente de análise`.
* Botão `Limpar conversa` no topo.
* Balões de mensagem em cards brancos com borda sutil, ícone identificador à esquerda (Avatar usuário em vermelho/coral suave, Avatar assistente em laranja/âmbar suave).
* Input de texto multi-linha (`textarea`) + botão verde primário `Enviar pergunta`.

---

## 4. Checklist de Informações Necessárias para Cada Nova Tela

Para que qualquer desenvolvedor ou IA crie uma nova tela dentro do padrão no Hackathon, preencha este briefing mínimo:

1. **Identificação da Tela:**
   * Categoria no menu (`Principal`, `Análise` ou `Operação`)
   * Nome da tela no menu e no Breadcrumb
   * Kicker (ex: `OPERAÇÃO / INGESTÃO`)
   * Título (`H1`) e Subtítulo (1 frase)
2. **Fonte de Dados e Atualização:**
   * Origem (ex: tabela do DuckDB ou webhook n8n)
   * Precisa do botão `Recarregar dados`? (Sim/Não)
3. **Filtros Necessários (Recorte):**
   * Quais campos filtram a tela? (Máximo recomendado: 3 a 5 filtros)
4. **KPIs Principais (Máximo 4 cards):**
   * Para cada card: *Título*, *Métrica/Cálculo* e *Texto auxiliar*.
5. **Área Principal (Core da Tela):**
   * Qual o componente central? (Gráfico Treemap, Formulário de Ingestão, Lista de Curadoria, Tabela Editável, etc.)
6. **Ações e Exportação:**
   * Quais botões de ação existem? (Ex: Salvar, Aprovar, Exportar CSV, Acionar Workflow n8n).