# Proposta 2.0 — Design System e Arquitetura UI/UX para Plataforma Empresarial em Streamlit

Versão: 2.0\
Tecnologia: Python + Streamlit\
Aplicação: Plataforma corporativa de análise de dados e apoio à tomada de decisão\
Público-alvo: Gestores, analistas, coordenadores e tomadores de decisão\
Identidade visual: Azul-petróleo `#293943` e verde tecnológico `#2DAC8A`\
Diretriz: Interface corporativa moderna, responsiva, intuitiva, dinâmica e orientada a resultados.

## 1. Objetivo da proposta

Desenvolver uma plataforma empresarial de análise de dados utilizando Streamlit, mas com uma identidade visual própria, evitando a aparência tradicional das aplicações desenvolvidas com essa biblioteca.

A interface deverá combinar:

- Sobriedade corporativa: aparência profissional, adequada à apresentação de informações estratégicas.
- Modernidade tecnológica: componentes contemporâneos, organização visual consistente e microinterações discretas.
- Dinamismo: filtros interativos, gráficos responsivos e atualização contextual das informações.
- Intuitividade: navegação simples, redução da carga cognitiva e acesso rápido às funcionalidades principais.
- Eficiência analítica: priorização de indicadores, comparações e informações que auxiliem decisões.
- Acessibilidade: contraste adequado, navegação por teclado e comunicação visual independente exclusivamente de cores.
- Desempenho: respostas rápidas, processamento otimizado e carregamento progressivo.

O objetivo não é apenas tornar o Streamlit visualmente mais atraente, mas transformá-lo em um ambiente de trabalho executivo, no qual o usuário consiga compreender os dados, identificar desvios e tomar decisões com o menor esforço possível.

## 2. Identidade visual e harmonia de cores

### 2.1. Paleta principal

| Cor               | Código hexadecimal | Aplicação                                |
| ----------------- | ------------------ | ---------------------------------------- |
| Azul-petróleo     | `#293943`          | Identidade visual, navegação e estrutura |
| Verde tecnológico | `#2DAC8A`          | Marca, ações e destaques                 |
| Azul analítico    | `#47758A`          | Gráficos e informações secundárias       |
| Verde suave       | `#E8F4F0`          | Destaques sutis e fundos informativos    |
| Cinza gelo        | `#F5F8FA`          | Fundo principal no tema claro            |

O azul-petróleo transmite estabilidade e confiança. O verde tecnológico introduz modernidade e dinamismo sem comprometer a seriedade da interface.

### 2.2. Configuração dos temas

| Elemento            | Tema claro | Tema escuro |
| ------------------- | ---------- | ----------- |
| Fundo principal     | `#F5F8FA`  | `#141E24`   |
| Cards e painéis     | `#FFFFFF`  | `#202D35`   |
| Menu lateral        | `#293943`  | `#19252C`   |
| Texto principal     | `#293943`  | `#EAF1F3`   |
| Texto secundário    | `#60737E`  | `#A9BBC3`   |
| Bordas e divisórias | `#DCE5E9`  | `#35464F`   |
| Botões e ações      | `#23876D`  | `#46C6A1`   |
| Azul secundário     | `#47758A`  | `#75A9BF`   |
| Fundo de destaque   | `#E8F4F0`  | `#243F3A`   |

Diretriz de implementação: utilizar tokens semânticos de cores, evitando códigos hexadecimais distribuídos diretamente pelos componentes.

Isso permite alternar entre os temas sem modificar individualmente os elementos da interface.

### 2.3. Cores semânticas

| Estado     | Tema claro | Tema escuro | Significado                 |
| ---------- | ---------- | ----------- | --------------------------- |
| Sucesso    | `#23876D`  | `#46C6A1`   | Resultados positivos        |
| Informação | `#377CA1`  | `#75B8DE`   | Informações complementares  |
| Atenção    | `#B7791F`  | `#E9B65E`   | Desvios e pontos de atenção |
| Crítico    | `#C6535A`  | `#F08086`   | Falhas e riscos relevantes  |

As cores de estado devem ser utilizadas apenas quando houver significado analítico, evitando confundir a identidade visual da marca com o desempenho dos indicadores.

### 2.4. Proporção de utilização

| Categoria         | Proporção aproximada | Aplicação                                   |
| ----------------- | -------------------- | ------------------------------------------- |
| Cores neutras     | 60%                  | Fundos, superfícies e áreas de leitura      |
| Cores estruturais | 25%                  | Menus, cabeçalhos e navegação               |
| Cores de destaque | 15%                  | Botões, indicadores e elementos interativos |

Essa distribuição é uma referência visual, não uma regra rígida.

## 3. Arquitetura visual da aplicação

A organização recomendada é composta por quatro regiões principais:

1. Barra superior (Topbar): identidade da plataforma, contexto da página, atualização dos dados e controles globais.
2. Menu lateral (Sidebar): navegação persistente entre áreas funcionais.
3. Área principal (Workspace): indicadores, gráficos, tabelas e análises.
4. Painel contextual: filtros avançados, detalhes de indicadores e informações complementares, exibidos somente quando necessários.

### 3.1. Hierarquia visual

A estrutura deve seguir esta organização:

```
┌────────────────────────────────────────────────────────────────────┐
│ TOPBAR                                                             │
│ Logotipo | Nome da plataforma | Atualização | Tema | Perfil        │
├────────────────┬───────────────────────────────────────────────────┤
│                │                                                   │
│ SIDEBAR        │ WORKSPACE                                         │
│                │                                                   │
│ Visão geral    │ Título da página                                  │
│ Indicadores    │ Descrição e contexto                              │
│ Explorar dados │                                                   │
│ Comparativos   │ [Filtros globais]                                 │
│ Relatórios     │                                                   │
│                │ [KPI 1] [KPI 2] [KPI 3] [KPI 4]                  │
│                │                                                   │
│                │ [Gráfico principal]  [Gráfico comparativo]        │
│                │                                                   │
│                │ [Tabela analítica / Diagnóstico]                  │
│                │                                                   │
│                │ [Alertas e ações recomendadas]                    │
│                │                                                   │
│ Configurações  │                                                   │
├────────────────┴───────────────────────────────────────────────────┤
│ RODAPÉ DISCRETO                                                    │
└────────────────────────────────────────────────────────────────────┘
```

A interface real deverá adaptar a navegação e a distribuição dos componentes ao tamanho da tela.

### 3.2. Barra superior (Topbar)

A Topbar deve permanecer visualmente consistente entre todas as páginas.

| Elemento            | Função                                     |
| ------------------- | ------------------------------------------ |
| Logotipo            | Identificação da plataforma                |
| Título da página    | Orientação contextual                      |
| Última atualização  | Transparência sobre a atualidade dos dados |
| Notificações        | Alertas relevantes                         |
| Alternância de tema | Seleção entre claro e escuro               |
| Perfil              | Identificação e preferências do usuário    |

Evitar excesso de informações na Topbar.

O objetivo é oferecer orientação e controles globais sem disputar a atenção com os dados.

### 3.3. Menu lateral (Sidebar)

O menu deve utilizar uma organização funcional, não uma lista extensa de páginas técnicas.

| Grupo     | Página          | Objetivo                            |
| --------- | --------------- | ----------------------------------- |
| Principal | Visão executiva | Resumo dos indicadores estratégicos |
| Análise   | Indicadores     | Acompanhamento de KPIs              |
| Análise   | Explorar dados  | Investigação detalhada              |
| Análise   | Comparativos    | Análise entre períodos ou segmentos |
| Gestão    | Relatórios      | Consulta e exportação               |
| Sistema   | Configurações   | Preferências e administração        |

As opções devem ser ajustadas às funcionalidades efetivamente existentes no projeto.

Comportamentos recomendados:

- Ícones consistentes.
- Destaque visual da página ativa.
- Menu recolhível.
- Agrupamento de funcionalidades relacionadas.
- Navegação preservando o contexto do usuário.
- Identificação clara da seção atual.

### 3.4. Área principal (Workspace)

A área principal deve seguir a hierarquia:

Contexto → Indicadores → Tendências → Diagnóstico → Ação.

Essa organização responde progressivamente às perguntas do gestor:

1. Qual é a situação atual?
2. O desempenho está melhorando ou piorando?
3. Onde estão os desvios?
4. O que explica os resultados?
5. Que decisão precisa ser tomada?

O usuário não deve precisar percorrer diversas páginas para compreender o estado geral do negócio.

## 4. Estrutura de páginas e componentes

### 4.1. Dashboard executivo

A página inicial deve apresentar uma visão consolidada do desempenho.

| Região                 | Conteúdo                         | Comportamento                       |
| ---------------------- | -------------------------------- | ----------------------------------- |
| Cabeçalho              | Título, descrição e atualização  | Persistente e contextual            |
| Filtros globais        | Período, unidade e segmento      | Aplicados aos indicadores da página |
| Indicadores principais | KPIs e variações                 | Cards com valores e tendências      |
| Análise temporal       | Evolução dos indicadores         | Gráficos interativos                |
| Comparativos           | Resultados por categoria         | Gráficos e tabelas                  |
| Alertas                | Desvios e situações críticas     | Ordenação por relevância            |
| Detalhamento           | Dados analíticos                 | Expansão sob demanda                |
| Ações                  | Exportação e acesso a relatórios | Botões contextuais                  |

A página deve apresentar inicialmente os resultados mais importantes, permitindo aprofundamento progressivo.

### 4.2. Cards de indicadores (KPI Cards)

Os indicadores devem utilizar componentes personalizados, evitando depender exclusivamente da aparência padrão de `st.metric`.

Cada card deve conter:

- Nome do indicador.
- Valor atual.
- Unidade de medida.
- Variação em relação ao período de referência.
- Representação visual da tendência, quando útil.
- Indicação de meta, quando existente.
- Acesso ao detalhamento.

Diretrizes visuais:

| Propriedade         | Recomendação                      |
| ------------------- | --------------------------------- |
| Fundo               | Superfície correspondente ao tema |
| Bordas              | 1 px, discretas                   |
| Cantos              | Raio de 10–12 px                  |
| Espaçamento interno | 16–24 px                          |
| Valor principal     | 24–32 px                          |
| Nome do indicador   | 12–14 px                          |
| Variação            | 12–14 px                          |
| Sombra              | Muito sutil ou ausente            |
| Interatividade      | Tooltip ou acesso ao detalhamento |

Não utilizar verde automaticamente para qualquer variação positiva.

O significado da variação depende do indicador: aumento de custos ou falhas, por exemplo, pode ser desfavorável.

### 4.3. Gráficos analíticos

Recomendo utilizar Plotly como biblioteca principal de visualização, por sua integração com Streamlit e capacidade de apresentar gráficos interativos.

Diretrizes:

- Remover fundos e bordas desnecessários.
- Aplicar a paleta visual da plataforma.
- Manter legendas e títulos consistentes.
- Utilizar tooltips com informações contextualizadas.
- Padronizar unidades, escalas e formatação numérica.
- Evitar excesso de séries simultâneas.
- Permitir seleção de períodos e categorias.
- Utilizar cores semânticas apenas quando houver significado.

O gráfico deve apresentar a informação de maneira clara antes de exigir qualquer interação.

### 4.4. Tabelas analíticas

As tabelas devem ser adequadas ao trabalho de análise detalhada.

Funcionalidades recomendadas:

- Ordenação por coluna.
- Filtros contextuais.
- Pesquisa por texto, quando aplicável.
- Formatação de valores e unidades.
- Destaque de situações críticas.
- Paginação ou virtualização para grandes volumes.
- Exportação dos dados filtrados.
- Seleção de registros para detalhamento.

Utilizar `st.dataframe` como ponto de partida, configurando suas colunas, formatos e comportamento.

Quando forem necessárias funcionalidades mais avançadas, avaliar componentes especializados.

## 5. Sistema de layout e espaçamento

### 5.1. Grid de interface

Recomendo um sistema de espaçamento baseado em múltiplos de 4 px, com unidade principal de 8 px.

| Elemento                       | Espaçamento recomendado |
| ------------------------------ | ----------------------- |
| Espaçamento mínimo             | 4 px                    |
| Entre ícone e texto            | 8 px                    |
| Entre elementos relacionados   | 12–16 px                |
| Espaçamento interno dos cards  | 16–24 px                |
| Entre cards                    | 16–24 px                |
| Entre seções                   | 24–32 px                |
| Margens da área principal      | 24–32 px                |
| Separação entre grandes blocos | 32–48 px                |

O espaçamento deve comunicar a relação entre os elementos.

### 5.2. Dimensões estruturais

| Componente             | Dimensão de referência          |
| ---------------------- | ------------------------------- |
| Topbar                 | 64–72 px de altura              |
| Sidebar expandida      | 240–264 px de largura           |
| Sidebar recolhida      | 64–72 px de largura             |
| Área principal         | Largura flexível                |
| Conteúdo analítico     | Máximo sugerido de 1600–1800 px |
| Cards de indicadores   | Altura aproximada de 120–160 px |
| Botões e campos        | Altura de 40–44 px              |
| Cantos dos componentes | 8–12 px                         |

Essas medidas são referências de design, não limitações rígidas.