<p align="center">
  <img src="./docs/assets/social_media_wallpaper.jpg" width="100%"  alt="Capa do projeto" />
</p>

---

# 🚀 CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais

---

## Descrição
O **CommunityLab** é um ecossistema inteligente de automação projetado para transformar o fluxo contínuo de discussões e dúvidas de comunidades técnicas em ativos estruturados de valor educacional e marketing.

Projeto desenvolvido pelo **Grupo 14 - Turma G10** para o Hackathon ONE - G10 Brasil, do programa **ONE - Oracle Next Education**.

---

## Sumário

* [1. Objetivo](#1-objetivo)
* [2. Tecnologias](#2-tecnologias)
* [3. Arquitetura](#3-arquitetura)
* [4. Estrutura de Diretórios](#4-estrutura-de-diretórios)
* [5. Como Executar](#5-como-executar)
* [6. Fluxo Git e Contribuição](#6-fluxo-git-e-contribuição)
* [7. Cronograma Geral](#7-cronograma-geral)
* [8. Equipe](#8-equipe)

---

## 1. Objetivo

Desenvolver um MVP funcional capaz de ingerir dados de comunidades, orquestrar triagens com IA, permitir curadoria humana (*Human-in-the-Loop*) e persistir pacotes de conteúdo estruturados na nuvem OCI.

---

## 2. Tecnologias

* **Linguagem:** Python 3.11+
* **Interface / Curadoria:** Streamlit
* **Engenharia de Dados:** DuckDB, Pandas, JSON Schema
* **Orquestração:** n8n (Docker)
* **Modelos de IA:** Google Gemini API (Camada Gratuita) / Groq ou Ollama
* **Cloud & Armazenamento:** Oracle Cloud Infrastructure (OCI Object Storage Always Free)

---

## 3. Arquitetura

<p align="center">
  <img src="./docs/assets/arquitetura-conceitual.png" alt="Arquitetura conceitual do pipeline multicanal" />
  <br>
  <em>Fig.01 - Arquitetura conceitual do pipeline multicanal</em>
</p>

---

## 4. Estrutura de Diretórios

```
├── 📁 .github/                                # Governança do GitHub
│   |
│   └── 📄 PULL_REQUEST_TEMPLATE.md            # Template para criação de PR
│
├── 📁 data/                                   # Estrutura e contratos de dados
│   ├── 📁 raw/                                # Dados brutos baixados (conteúdo ignorado via .gitignore)
│   ├── 📁 processed/                          # Dados pós-processamento/DuckDB (conteúdo ignorado via .gitignore)
│   ├── 📁 schemas/                            # Contratos JSON Schema obrigatórios
│   └── 📁 samples/                            # Exemplos de teste
│
├── 📁 docs/                                   # Documentação técnica e governança
│   ├── 📁 adr/                                # Registro de decisões arquiteturais
│   ├── 📁 assets/                             # Imagens, fluxogramas e diagramas da documentação
│   ├── 📁 meetings/                           # Atas das reuniões e rituais ágeis
│   ├── 📁 specs/                              # Especificações funcionais e técnicas (SDDs)
│   ├── 📄 guia_github_projects.md             # Guia de uso do GitHub Projects e padrões de branches, commits e PRs para o time
│   └── 📄 escopo_projeto.md                    # Especificação do escopo e requisitos
│
├── 📁 n8n/                                    # Orquestração e workflows locais
│   ├── 📁 workflows/                          # Fluxos exportados em JSON
│   └── 📄 docker-compose.yml                  # Configuração do container n8n self-hosted
│
├── 📁 references/                             # Materiais de consulta do projeto
│
├── 📁 src/                                    # Código-fonte da aplicação
│   ├── 📁 pipeline/                           # Ingestão, processamento e validações
│   ├── 📁 services/                           # Integrações com serviços externos
│   ├── 📁 utils/                              # Funções utilitárias e helpers
│   └── 📁 views/                              # Telas e interfaces modulares do Streamlit
│
├── 📁 tests/                                  # Testes automatizados
│
├── 📄 .editorconfig                           # Padronização de estilo de formatação entre diferentes editores e IDEs
├── 📄 .env.example                            # Modelo de exemplo de variáveis de ambiente
├── 📄 .gitignore                              # Regras de arquivos e diretórios ignorados pelo Git
├── 📄 LICENSE                                 # Termos de licença de uso e distribuição do projeto
├── 📄 README.md                               # Apresentação do projeto e instruções de inicialização
└── 📄 requirements.txt                        # Dependências e bibliotecas Python do projeto

```

---

## 5. Como Executar

**Pré-requisitos:**

* Python 3.11+
* Git

1. Clonar o repositório e acessar a branch `develop`
```bash
git clone <URL_DO_REPOSITORIO>
cd G10-BRASIL-Equipe-14
git checkout develop
```

2. Configurar o ambiente virtual Python
```bash
python -m venv .venv

# Linux / macOS:
source .venv/bin/activate

# Windows:
.venv/Scripts/Activate
```

3. Instalar dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt

```

---

## 6. Fluxo Git e Contribuição

<p align="left>
<a href="https://github.com/orgs/No-Country-simulation/projects/565/views/1">
    <img src="https://img.shields.io/badge/GitHub_Project-Kanban-1074e7?style=flat-square&logo=github&logoColor=white" alt="Kanban do Projeto" />
</a>
</p>

* Desenvolvimento iterativo gerenciado pelo quadro Kanban no GitHub Projects pela equipe

* **Branch principal de trabalho:** `develop` (a branch `main` é protegida).

* **Nomenclatura de branches:** `feat/S0-XX-descricao`, `fix/S0-XX-descricao`, `docs/S0-XX-descricao`.

* **Commits:** Siga o padrão de Commit Semântico (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `build:`, `chore:`) e adicione (#número-da-issue) para realizar o link do commit com a task.

* **Nomenclatura de commits:** `[S0-XX] feat: descricao-commit (#1)`, `[S0-XX] fix: descricao-commit (#1)`, `[S0-XX] docs: descricao-commit (#1)`

* Toda PR deve usar o template fornecido em `.github/PULL_REQUEST_TEMPLATE.md`, sendo preciso ao menos **1 aprovação** para ser integrada à `develop`.

* Em caso de dúvidas, não exite em perguntar no grupo do discord.

---

## 7. Cronograma Geral

| Etapa | Data/Período | Foco |
|---|---|---|
| Semana 0 | 12/10/2026 a 18/10/2026 | Alinhamento estratégico, documentação inicial e configurações base | 
| Semana 1 | 19/10/2026 a 25/10/2026 | Engenharia de prompts, datasets e ingestão |
| Semana 2 | 26/10/2026 a 01/11/2026 | Orquestração condicional n8n e Módulos da interface | 
| Semana 3 | 02/11/2026 a 08/11/2026 | Geração consolidada, persistência e curadoria |
| Semana 4 | 09/11/2026 a 15/11/2026 | Homologação, OCI Compute e revisão
| Semana 5 | 16/11/2026 a 22/11/2026 | Documentação, preparação da apresentação e revisão final |
| Demo Day 1 | 24/11/2026 | Apresentação
| Demo Day 2 | 26/11/2026 | Apresentação

---

## 8. Equipe

[David Lima](https://github.com/DavidLimm)

[Gustavo Silva](https://github.com/Gustavotuur)

[Michael Dambock](https://github.com/dammi01)

[Ricieri Rosa](https://github.com/garcezrosa)

[Rodrigo Aguiar](https://github.com/RAguiarEng)

[Rodrigo Silva](https://github.com/prospera-analytics)

[Vitor Pires](https://github.com/vikpires)
