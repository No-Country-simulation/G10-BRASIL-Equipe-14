# Guia Rápido: Como Usar o GitHub Projects no CommunityLab

Este guia orienta o uso do **GitHub Projects** para acompanhar o progresso das tarefas de forma visual e sincronizada com o código.

---

## 1. Conceitos Básicos

* **Issue**: É o "card" da tarefa. Contém a descrição, o responsável e o checklist de entrega (*Definition of Done*).

* **Project (Quadro)**: O painel visual onde organizamos todas as issues em colunas (estilo Kanban) ou tabelas.

* **Milestone**: O marco temporal (nossas semanas de entrega: *Semana 0* até *Semana 6*).

* **Assignee**: A(s) pessoa(s) responsável(is) por executar e entregar a tarefa.

---

## 2. Rotina Diária: Como Trabalhar com as Tarefas (tasks)

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

* Exemplo de Estrutura de branches:
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

* Após o PR ser aprovado e mesclado (*squash/merge*), o card vai automaticamente para a coluna **Done** (Concluído). Se não for automático, arraste-o manualmente.

---

## 3. Visualizações Mais Úteis

Você pode alternar as abas no topo do projeto:

1. **Board (Kanban)**: A visualização em colunas clássica (`Backlog` $\rightarrow$ `To Do` $\rightarrow$ `In Progress` $\rightarrow$ `In Review` $\rightarrow$ `Done`). Ideal para as reuniões diárias (*dailies*).

2. **Table (Tabela)**: Exibe todas as tarefas como uma planilha. Ótima para filtrar por responsável ou ordenar por semana.

3. **Roadmap (Gantt)**: Linha do tempo visual mostrando quando cada semana/sprint começa e termina.

---

## 4. Dicas

* **Filtre por você mesmo**: No campo de busca do projeto, digite `assignee:@me` para ver instantaneamente apenas as suas tarefas.

* **Mantenha o card atualizado**: Se travou em algo, deixe um comentário na issue marcando o colega com `@usuario` para pedir ajuda.

* **Critério de Aceite (DoD)**: Só passe uma tarefa para *Done* se todos os itens da descrição dela tiverem sido testados e a documentação associada atualizada.