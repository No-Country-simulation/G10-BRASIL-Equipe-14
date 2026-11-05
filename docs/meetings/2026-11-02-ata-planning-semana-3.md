# 📝 Ata de Reunião — Sprint Planning / Daily (Semana 3)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 02 de Novembro de 2026 (Segunda-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva, Ricieri Rosa

---

## 1. Objetivo da Reunião

Alinhamento das atividades iniciais do projeto na **Semana 3**, que será focado na Geração Consolidada, Persistência e Curadoria. Além disso, foi realizada a daily para alinhar as atividades realizadas ao longo do dia e final de semana, atividades previstas, impedimentos e dificuldades encontradas. 

---

## 2. Resumo Executivo

A equipe realizou uma reunião de planejamento semanal (_Sprint Planning_) e alinhamento diário (_daily_) de acompanhamento do projeto em **02/11/2026** para avaliar o andamento das tarefas da Semana 2 e o planejamento da Semana 3. **Vitor** concluiu os testes e a refatoração do código da Pull Request (PR) de _prompts_ originalmente criada pelo Gustavo, dividindo arquivos extensos em funções modulares e utilitários na pasta `utils`, além de adicionar _guardrails_ de segurança e anonimização de dados pessoais/chaves e incluir a fonte Hacker News na pipeline. **Rodrigo** atualizou a documentação de credenciais e _workflows_ no n8n (`docs/specs`), disponibilizou uma versão funcional do fluxo S201 com nós de LLM (limitando a 1 item para economizar _tokens_ nos testes) e sugeriu fixar tópicos da área _tech_ no _front-end_ em vez de manter buscas totalmente abertas. **Michael** efetuou ajustes no arquivo `config.py` para sincronizar os parâmetros padrão (`default_time`) e avançou na preparação do módulo de integração com a Oracle Cloud (OCI).

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Concluiu a refatoração da PR de _prompts_ do Gustavo, separando o código em arquivos e funções dentro da pasta `utils`. Implementou _guardrails_ de segurança no prompt (proteção contra _prompt injection_ e anonimização de dados como chaves de API, senhas e PII). Adicionou o Hacker News junto ao Mastodon e Stack Overflow na pipeline. Revisou a PR de Streamlit enviada pelo Ricieri.

- **Para amanhã/Próximos passos:** Subir a PR refatorada com os _guardrails_ e as três fontes de dados integradas. Revisar as três PRs recém-submetidas pelos colegas de equipe e organizar as tarefas do Kanban da Semana 3. Mencionou restrição de tempo temporária por conta das avaliações na faculdade.

#### **Rodrigo Aguiar**

- **Feito hoje:** Atualizou o arquivo de credenciais do n8n em `docs/specs` com a tabela e _paths_ das requisições principais de triagem/avaliação. Disponibilizou uma versão funcional do fluxo S201 no n8n com nós de LLM integrados, aplicando uma trava para limitar a avaliação a 1 item por teste e economizar _tokens_.

- **Para amanhã / Próximos passos:** Avançar na tarefa S202/S203 de automação dos nós condicionais de roteamento no n8n. Propor ao time a fixação de categorias _tech_ no _front-end_ (como mobile, back-end, front-end, DevOps, data analysis) para delimitar o escopo de busca e evitar dispersão.

#### **Michael Dambock**

- **Feito hoje:** Atualizou o arquivo `config.py` ajustando os parâmetros padrão de tempo (`default_time`) conforme repassado por Rodrigo. Iniciou o desenvolvimento do módulo de conexão e integração com CI/CD e com a infraestrutura da OCI.

- **Para amanhã / Próximos passos:** Concluir a integração do módulo com a OCI e disponibilizar os conectores para a equipe. Compartilhou com o time a leitura sobre a publicação SDD 2.0 (Google - _Elephant & Goldfish_).

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                        | Responsável     | Prazo / Status              |
| :-------------------------------------------------------------------------- | :-------------- | :-------------------------- |
| Subir a PR refatorada de _prompts_ com _guardrails_ e suporte a Hacker News | Vitor           | Hoje à noite / Em andamento |
| Revisar as três PRs pendentes no repositório                                | Vitor           | Próximos passos             |
| Fixar tópicos e categorias _tech_ predefinidas para a busca no _front-end_  | Rodrigo e Vitor | Definido / A implementar    |
| Implementar nós condicionais de roteamento no n8n (tarefa da Semana 2)      | Rodrigo         | Em andamento                |
| Finalizar o módulo de conexão com a OCI e integração CI/CD                  | Michael         | Em andamento                |
| Revisar e atualizar os _cards_ no Kanban do GitHub Projects para a Semana 3 | Toda a equipe   | Em andamento                |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 03 de Novembro de 2026 (Terça-feira)

- **Horário:** 19h30
