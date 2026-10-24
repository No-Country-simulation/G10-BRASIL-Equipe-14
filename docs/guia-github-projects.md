# Guia Rápido: Como Usar o GitHub Projects no CommunityLab

Este guia orienta o uso do **GitHub Projects** para acompanhar o progresso das tarefas de forma visual e sincronizada com o código.

---

## Sumário

- [1. Conceitos Básicos](#1-conceitos-básicos)
- [2. Criação de Issues (Template Padrão)](#2-criação-de-issues-template-padrão)
- [3. Rotina Diária: Como Trabalhar com as Tasks](#3-rotina-diária-como-trabalhar-com-as-tasks)
- [4. Visualizações Mais Úteis](#4-visualizações-mais-úteis)
- [5. Boas Práticas](#5-boas-práticas)

---

## 1. Conceitos Básicos

- **Issue**: É o "card" da tarefa. Contém a descrição, o responsável e o checklist de entrega (*Definition of Done*).

- **Project (Quadro)**: O painel visual onde organizamos todas as issues em colunas (estilo Kanban) ou tabelas.

- **Milestone**: O marco temporal (nossas semanas de entrega: *Semana 0* até *Semana 6*).

- **Assignee**: A(s) pessoa(s) responsável(is) por executar e entregar a tarefa.

---


## 2. Criação de Issues (Template Padrão)

### Passo 1: Localizar o Template no Repositório

1. No menu superior do repositório no GitHub, acesse a aba Issues.

2. Clique no botão verde New issue (canto superior direito).

3. Na lista de templates disponíveis, localize Task / Tarefa e clique no botão Get started.

### Passo 2: Ajustar o Título da Issue

O título já virá pré-preenchido com a convenção de nomenclatura do projeto:

```text
[SX-XX] [Área]: <Nome conciso da tarefa>
```

- Substitua `[SX-XX]` pelo identificador da sprint e número do item (ex.: [S1-01]).

- Substitua `[Área]` pelo contexto funcional correspondente, como:
  - [Automação]  
  - [Backend]
  - [Data Science]
  - [Eng. Dados]
  - [Equipe]
  - [Gestão]  
  - [Infra]  
  - [QA]
  - [UI]

- Adicione um título claro que descreva o entregável. 

Exemplo: [S1-01] [Eng. Dados] Especificar Schemas JSON de Entrada e Saída

### Passo 3: Detalhar a Descrição
Preencha seção principal do corpo da issue:

- Descrição da Tarefa: Especifique o que deve ser desenvolvido, ajustado ou configurado de forma clara e objetiva.

```markdown
Ex.:

### Descrição

- Elaborar ou revisar a documentação do projeto na Semana X, incluindo revisões do escopo, arquitetura do projeto, fontes de dados e elaboração de documentos adicionais, se necessário.

```

### Passo 4: Definir os Critérios de Aceitação (DoD - Definition of Done)
Liste os requisitos obrigatórios para que a tarefa seja considerada concluída. Mantenha os itens em formato de lista Markdown (`- [ ]`) para que se tornem checkboxes interativos:

```markdown
Ex.:

### Critérios de Aceitação (DoD)

- [ ] Revisão da documentação principal: escopo do projeto, especificações de arquitetura,  
- [ ] Adicionar documentação adicional (se houver): guias, ADRs, Specs ou similar.
- [ ] Arquivos salvos no diretório de documentação: Arquivos de documentação gerados e disponibilizados no diretório `docs/`, preferencialmente no formato Markdown (`.md`).
```

### Passo 5: Listar os metadados relacionados à tarefa
Descrever os componentes/módulos impactados, os artefatos gerados/alterados e a documentação de referência, se houver.

```markdown
### Metadados e Rastreabilidade

- **Componentes / Módulos impactados:** [ex.: APIs, Workflows, Schemas, Documentação]
- **Artefatos gerados/alterados:** [ex.: links de PRs, arquivos gerados, relatórios]
```

### Passo 6: Checklist de Entrega
Ao término da task, verificar se os requisitos foram atendidos. Mantenha os itens em formato de lista Markdown (`- [ ]`) para que se tornem checkboxes interativos:

```markdown
### Checklist de Entrega

- [ ] **Execução / Entrega principal concluída:** O objetivo central da tarefa foi executado e testado com sucesso.

- [ ] **Parâmetros e escopo validados:** Regras de negócio, limites, filtros ou requisitos definidos foram atendidos.

- [ ] **Validação de qualidade / formato:** Artefatos gerados, código ou documentos seguem os padrões estabelecidos do projeto.

- [ ] **Persistência / Registro:** Arquivos, saídas ou documentações foram devidamente versionados e disponibilizados no local correto.
```

### Passo 7: Conferir a Barra Lateral (Sidebar) e Publicar

Antes de submeter, confira a barra lateral direita do GitHub:

1. Assignees: Atribua a tarefa a você ou ao responsável pela execução.

2. **Labels:** Adicione a tag da área correspondente (Ex.: Eng Dados) e a atividade da task (enhancement, bug ou documentation).

3. **Projects:** Verifique se o card foi adicionado automaticamente ao quadro do projeto: "Kanban G10-Brasil-Equipe-14". Caso não tenha sido adicionado, selecione o projeto manualmente.

4. **Milestone:** Adicione o marco (milestone) referente à semana correspondente [Semana 0] a [Semana 6].

5. Clique no botão verde **Submit new issue**.

6. A nova issue irá sincronizar automaticamente no GitHub Projects na coluna **Backlog** no marco (milestone) correspondente.

---

## 3. Rotina Diária: Como Trabalhar com as Tasks

### Passo 1: Selecionar uma tarefa para fazer

1. Acesse a aba **Projects** no repositório da equipe e abra o projeto oficial.

2. Na coluna **Backlog**, localize a tarefa da semana atual atribua a você e mova o(s) card(s) que for fazer para **To Do** (A Fazer).

3. Arraste o card que estiver trabalhando para a coluna **In Progress** (Em Andamento).

### Passo 2: Criar a branch de trabalho

Nunca suba código direto na `main` ou na `develop`. Crie uma branch a partir da `develop` referenciando a tarefa:

```bash
# Atualize sua máquina com a develop
git checkout develop
git pull origin develop

# Crie sua branch com o padrão: tipo/ID-nome-curto
git checkout -b feat/S1-XX-webhook-n8n

```

- Exemplo de Estrutura de branches:
```
main (produção / releases estáveis)
  ↑
  └── develop (integração contínua da equipe)
        ↑
        ├── feat/S1-01-dataset-sintetico
        ├── feat/S1-02-prompt-router
        ├── fix/S3-02-webhook-oci-timeout
        └── docs/S0-01-project-model-canvas

```

### Passo 3: Fazer commits semânticos

Ao realizar commits, use o padrão da equipe citando o identificador da tarefa, a descrição do commit (de preferência em inglês) e o número correspondente da tarefa no github projects, sendo um número seguido de `#`, por exemplo, `#1` para a primeira task:

```bash
git commit -m "[S1-XX] feat: mensagem de commit (#número-da-issue)"

```
```bash
git commit -m "[S1-06] feat: add ingestion webhook and code node (#11)"

```

### Passo 4: Abrir o Pull Request (PR)

1. Suba sua branch para o GitHub:
```bash
git push -u origin feat/S1-XX-webhook-n8n

```

2. No GitHub, clique em **Compare & pull request** mirando a branch **`develop`**.

3. No corpo do PR, use uma palavra mágica para ligar o PR à issue:

>[!TIP] *Closes #12* ou *Fixes #12* (substitua pelo número da sua issue).

4. Ao criar a PR, o GitHub move a issue para a coluna **In Review** (Em Revisão). Marque pelo menos 1 colega para revisar.

### Passo 5: Concluir a tarefa

- Após o PR ser aprovado e mesclado (*squash/merge*), o card vai automaticamente para a coluna **Done** (Concluído). Caso não seja movido automaticamente após alguns segundos, arraste-o manualmente.

---

## 4. Visualizações Mais Úteis

Você pode alternar as abas no topo do projeto:

1. **Board (Kanban)**: A visualização em colunas clássica (`Backlog` $\rightarrow$ `To Do` $\rightarrow$ `In Progress` $\rightarrow$ `In Review` $\rightarrow$ `Done`). Ideal para as reuniões diárias (*dailies*).

2. **Table (Tabela)**: Exibe todas as tarefas como uma planilha. Ótima para filtrar por responsável ou ordenar por semana.

3. **Roadmap (Gantt)**: Linha do tempo visual mostrando quando cada semana/sprint começa e termina.

---

## 5. Boas Práticas

- **Filtre por você mesmo**: No campo de busca do projeto, digite `assignee:@me` para ver instantaneamente apenas as suas tarefas.

- **Mantenha o card atualizado**: Se travou em algo, deixe um comentário na issue marcando o colega com `@usuario` para pedir ajuda.

- **Critério de Aceite (DoD)**: Só passe uma tarefa para *Done* se todos os itens da descrição dela tiverem sido testados e a documentação associada atualizada.