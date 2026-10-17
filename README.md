# 🚀 CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais

O **CommunityLab** é um ecossistema inteligente de automação projetado para transformar o fluxo contínuo de discussões e dúvidas de comunidades técnicas em ativos estruturados de valor educacional e marketing.

Projeto desenvolvido pelo **Grupo 14** para o Hackathon ONE - G10 Brasil, do programa **ONE - Oracle Next Education**.

---

## Objetivo

Desenvolver um MVP funcional capaz de ingerir dados de comunidades, orquestrar triagens com IA, permitir curadoria humana (*Human-in-the-Loop*) e persistir pacotes de conteúdo estruturados na nuvem OCI.

---

## Estrutura de pastas:

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

## Tecnologias

* **Linguagem:** Python 3.11+
* **Interface / Curadoria:** Streamlit
* **Engenharia de Dados:** DuckDB, Pandas, JSON Schema
* **Orquestração:** n8n (Docker)
* **Modelos de IA:** Google Gemini API (Camada Gratuita) / Groq ou Ollama
* **Cloud & Armazenamento:** Oracle Cloud Infrastructure (OCI Object Storage Always Free)

---

## Execução do Ambiente

### 1. Clonar o repositório e acessar a branch `develop`
```bash
git clone <URL_DO_REPOSITORIO>
cd G10-BRASIL-Equipe-14
git checkout develop
```

### 2. Configurar o ambiente virtual Python
```bash
python -m venv .venv

# Linux / macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\Activate
```

### 3. Instalar dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt

```

---

## Fluxo Git e Contribuição

* **Branch principal de trabalho:** `develop` (a branch `main` é protegida).

* **Nomenclatura de branches:** `feat/S0-XX-descricao`, `fix/S0-XX-descricao`, `docs/S0-XX-descricao`.

* **Commits:** Siga o padrão de Commit Semântico (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `build:`, `chore:`) e adicione (#número-da-issue) para realizar o link do commit com a task.

* **Nomenclatura de commits:** `[S0-XX] feat: descricao-commit (#1)`, `[S0-XX] fix: descricao-commit (#1)`, `[S0-XX] docs: descricao-commit (#1)`

* Toda PR deve usar o template fornecido em `.github/PULL_REQUEST_TEMPLATE.md`, sendo preciso ao menos **1 aprovação** para ser integrada à `develop`.

* Em caso de dúvidas, não exite em perguntar no grupo do discord.
