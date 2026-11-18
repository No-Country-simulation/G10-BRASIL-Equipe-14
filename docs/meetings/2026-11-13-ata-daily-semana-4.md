# 📝 Ata de Reunião — Daily (Semana 4)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 13 de Novembro de 2026 (Sexta-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou a sua reunião diária (_daily_) em **13/11/2026** para acompanhar a integração da camada de banco de dados DuckDB, a refatoração e publicação de Pull Requests (PRs) e o alinhamento das tarefas finais do MVP. **Michael** e **Rodrigo** esclareceram que a inclusão do DuckDB não tem a finalidade de substituir o n8n ou fluxos existentes, mas sim de servir como uma camada intermediária de leitura eficiente para normalizar JSONs heterogêneos de múltiplos sites sem sobrecarregar a memória do sistema. Rodrigo apresentou as melhorias na interface do Streamlit (tarefa **S3-03**), incluindo a opção de download dos arquivos em `.zip` (pastas `raw/` e `processed/`) para backup/ingestão manual via Webhook WF05, enquanto as consultas automáticas de dados processados consomem diretamente do DuckDB conectado ao _bucket_ da OCI. No gerenciamento do código, **Vitor** enviou os PRs das tarefas **S1-04** e **S1-05**, iniciou a revisão da **S3-05** e orientou a equipe sobre a resolução de conflitos de _merge_ no arquivo `config.py` e branches concomitantes. Por fim, definiram-se os próximos passos para o painel de curadoria humana (tarefa **S3-04** de Ricieri) e a ampliação da coleta de dados para tópicos gerais como `career` (carreira) e áreas _tech_.


---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Subiu os PRs referentes às tarefas **S1-04** e **S1-05** (ajustes de prompts) e iniciou a revisão técnica da tarefa **S3-05** de Michael. Explicou a mecânica do Git na resolução de conflitos de _merge_ quando branches distintas alteram os mesmos arquivos base.

- **Para amanhã/Próximos passos:** Encerrar os ajustes das PRs **S1-04** e **S1-05** e aprovar os _commits_ pendentes.

#### **Rodrigo Aguiar**

- **Feito hoje:** Estruturou a integração do DuckDB no _frontend_ Streamlit, adicionando uma área de download/backup de arquivos zipados (`raw/` e `processed/`) via Webhook WF05 e a leitura direta via DuckDB conectado à OCI. Colocou em revisão as tarefas **S2-01**, **S2-02**, **S3-02**, **S3-03** e **S3-05**.

- **Para amanhã / Próximos passos:** Consultar a professora Brenda sobre a viabilidade de realizar postagens de teste em redes sociais reais (marcando os perfis dos membros e a instituição) e expandir a coleta de dados do n8n para tópicos gerais (como `career`, `front-end`, `back-end`, `devops`, `cloud` e `mobile`).

#### **Michael Dambock**

- **Feito hoje:**  Alinhou o papel funcional do DuckDB 2.0 (destacando o recurso `VARIANT` para a ingestão de JSONs heterogêneos sem necessidade de pré-conversão). Mencionou que a AWS adquiriu a DuckDB recente/recentemente e ressaltou os ganhos de velocidade de 30% na leitura de arquivos.

- **Para amanhã / Próximos passos:** Auxiliar Rodrigo no refinamento do painel de curadoria (**S3-04**) e na integração das métricas de sentimentos e tópicos (**S3-06**).

#### **Ricieri Rosa**

- **Feito hoje:** Confirmou a construção da estrutura base do painel de curadoria humana (tarefa **S3-04**) no Streamlit e pretende iniciar a task **S4-02**.

- **Para amanhã / Próximos passos:** Dar início à task **S4-02**.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                                | Responsável       | Prazo / Status             |
| :---------------------------------------------------------------------------------- | :---------------- | :------------------------- |
| Realizar o _merge_ da tarefa S103 para destravar a S1-04 e S1-05 no _develop_        | Vitor             | Prioritário / Em andamento |
| Conectar os fluxos de leitura do Streamlit à camada do DuckDB                       | Rodrigo e Ricieri | Em andamento               |
| Expandir a coleta do n8n para a tag `career` (carreira) e tópicos gerais            | Rodrigo           | Em andamento               |
| Revisar e vincular a tela do painel de curadoria humana (S3-04)                      | Ricieri e Michael | Em andamento               |
| Atualizar o diagrama de arquitetura do projeto no `README` com a inclusão do DuckDB | Vitor e Michael   | A realizar                 |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Sprint Planning (Início da Semana 5)

- **Data:** 16 de Novembro de 2026 (Segunda-feira)

- **Horário:** 19h30
