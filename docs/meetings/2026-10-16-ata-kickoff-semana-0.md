# 📝 Ata de Reunião — Alinhamento Estratégico e Kick-Off (Semana 0)

## Detalhes da Reunião
* **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10

- **Data:** 16 de Outubro de 2026 (Sexta-feira)

- **Participantes Presentes:** David Lima, Gustavo Silva, Michael Dambock, Rodrigo Silva, Ricieri Rosa, Vitor Pires

- **Assunto:** Definição do escopo, arquitetura, fluxos de trabalho e cronograma inicial do projeto no Community Lab.

---

## 1. Objetivo da Reunião

Alinhar a compreensão do desafio proposto pelo edital, definir o foco temático da solução, fechar o contrato de dados das fontes primárias, acordar as diretrizes do Git/GitHub e estabelecer o plano de ação imediato para a **Semana 0**.

---

## 2. Principais Decisões

### 2.1. Escopo e Solução Escolhida

* **Foco do MVP:** A equipe optou por focar no **Motor de FAQ Dinâmico e Conteúdo Educativo** (transformação de dúvidas e discussões técnicas em dicas rápidas, tutoriais e documentação).


* **Justificativa:** É a abordagem mais compatível com as fontes técnicas que serão consultadas e viabiliza a geração dos formatos de ativos exigidos (Post de LinkedIn + Newsletter/Highlights + FAQ Dinâmico).


### 2.2. Fontes de Dados e Ingestão

* **Fontes Base Iniciais:**

    * **Stack Exchange / Stack Overflow:** Para captura de dúvidas técnicas reais e discussões de código (foco inicial no tópico de *Inteligência Artificial* e *Programação*).

    * **Mastodon:** Alternativa de rede aberta com API gratuita para monitorar interações da comunidade sem custos de licença.

    * **Alternativa:** O dataset `LMSYS` (do Hugging Face) foi citado como plano de contingência caso haja escassez de dados nas APIs abertas.

* **Justificativa:** O grupo debateu restrições de APIs de redes como X (Twitter), Reddit e LinkedIn, optando por fontes com APIs/dados abertos e viáveis sem custos adicionais.

### 2.3. Ingestão de Dados

* **Tratamento e Limpeza:** Utilização de **DuckDB** para limpeza rápida, transformação e normatização dos dados brutos antes da entrega ao pipeline de IA.

* **Justificativa:** A abordagem reduz o consumo de memória RAM e processamento computacional, possibilitando o uso local sem a necessidade de manter um servidor de banco de dados pesado rodando.

### 2.4. Arquitetura e Engenharia de IA

* **Orquestrador de Fluxos:** **n8n local via Docker (self-hosted)** para gerenciar o webhook, o fluxo de nós condicionais e a triagem inicial.

    * Alternativa: scripts em Python ou *LangChain / LangGraph*, caso seja necessário complementar.

* **Provedores de LLM (Custo Zero):** Foco estrito em opções de custo zero para respeitar a gratuidade do programa ONE:


    * Google Gemini API (chave a ser disponibilizada para o projeto);


    * Groq API e endpoints gratuitos da Nvidia como alternativas de baixa latência;


    * Ollama avaliado para prototipagem local (ressalvando limites de lentidão/hardware).


* **Governança da IA (ADR / SSD):** Proposta de desenvolver arquivos de registro de decisões arquiteturais (Architecture Decision Record - `ADR`) e descrições estruturadas (Spec-Driven Development - `SSD`) para guiar os system prompts e evitar alucinações das LLMs, caso sejam adotados agentes de IA no desenvolvimento do projeto.

### 2.5. Persistência em Nuvem (OCI Always Free)

* **Object Storage:** Obrigatório para persistência dos JSONs de distribuição dos lotes. Será provisionado na conta individual de um integrante utilizando a camada Always Free.

* **OCI Compute (VM):** Ficará como item diferencial para a reta final, dadas as restrições de concorrência e memória das máquinas Always Free.


### 2.6. Governança do Repositório e Fluxo Git

1. **Proteção de Branches:**
    * A branch `main` ficará totalmente bloqueada para commits diretos (reservada apenas para a release final homologada).

    * A branch `develop` será o ambiente padrão de integração contínua.

2. **Pull Requests e Revisão Cruzada:**

    * Todo desenvolvimento deve ser feito em branches específicas de tasks.

    * Obrigatoriedade de **pelo menos 1 aprovação** (review) por outro colega antes de fazer o squash/merge na `develop` para garantir a verificação do código e prevenir eventuais conflitos.

3. **GitHub Projects:** 
    * Uso do quadro Kanban (*Backlog*, *To Do*, *In Progress*, *In Review*, *Done*) com atribuição individual de responsáveis.

    * Atribuição de tags/labels para funções específicas (Gestão, Cloud, Automação, Dados, Data Science, etc.).

---

## 3. Próximos Passos

- **Ações Imediatas (Semana 0):**
  - Ajuste do repositório no GitHub (Branches, Proteções e Templates).
  - Estrutura de diretórios e dependências
  - Definição formal e disponibilização do guia/documentação interna.
  - Provisionamento inicial do ambiente (OCI Bucket e container Docker com n8n).

---

## 4. Próxima Reunião

* **Reunião Obrigatória:** Sprint Planning (Início da Semana 1)

* **Data:** 19 de Outubro de 2026 (Segunda-feira)

* **Horário:** Horário a definir por votação no Discord.