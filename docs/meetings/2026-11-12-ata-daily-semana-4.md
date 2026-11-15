# 📝 Ata de Reunião — Daily (Semana 4)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 12 de Novembro de 2026 (Quinta-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Rodrigo Aguiar
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva, Ricieri Rosa, Vitor Pires

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou a sua reunião diária (_daily_) em **12/11/2026** para alinhar a arquitetura de integração de dados entre os fluxos do n8n, o armazenamento em nuvem e a interface gráfica em Streamlit. A principal decisão técnica da reunião foi a adoção do **DuckDB** (explorando o recurso `VARIANT` da versão 2.0 para manipulação de JSONs heterogêneos) como camada intermediária de leitura e consulta. Em vez de conectar a interface Streamlit diretamente aos _webhooks_ do n8n, o DuckDB consumirá os arquivos JSON diretamente dos diretórios do _bucket_ (`raw/`, `processed/` e `routing/`), entregando dados estruturados para as telas desenvolvidas por Ricieri. Além disso, reformatou-se o entendimento de que a ingestão de dados funcionará de forma 100% automática no MVP, e propôs-se a criação de um _dashboard_ administrativo no Streamlit para monitoramento de volume por estágio de processamento.

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Michael Dambock**

- **Feito hoje:** Moveu a tarefa **S3-05** para o status _"In Review"_. Apresentou a proposta técnica de utilizar o DuckDB 2.0 com suporte a dados JSON heterogêneos (`VARIANT`) para servir como ponte de leitura entre os arquivos no _bucket_ da OCI e o _frontend_ Streamlit.

- **Para amanhã / Próximos passos:** Documentar a solução com DuckDB na issue **S3-03**, conectar as consultas do DuckDB às pastas `raw/`, `processed/` e `routing/`, enviar links de referência (DuckPad e execução no navegador) e repassar a transcrição para a estruturação da documentação.

#### **Rodrigo Aguiar**

- **Feito hoje:** Realizou o _commit_ da tarefa **S3-03** (Issue #20), integrando os requisitos das tarefas **S2-01** (#13), **S2-02** (#14) e **S3-02** (#19). Atualizou os _workflows_ no n8n e registrou a documentação detalhando a atuação das rotas de _download_ (WF05) e de consulta por requisição (WF12).

- **Para amanhã / Próximos passos:** Publicar o comentário consolidado na issue **S3-03** e realizar requisições fracionadas ao longo do dia para popular as pastas do _bucket_ com novos tópicos além de Inteligência Artificial e Docker.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                                                    | Responsável       | Prazo / Status             |
| :------------------------------------------------------------------------------------------------------ | :---------------- | :------------------------- |
| Publicar o comentário consolidado na issue S3-03 detalhando as integrações com as tarefas #13, #14 e #19 | Rodrigo           | Prioritário / Em andamento |
| Conectar o DuckDB às pastas do _bucket_ (`raw/` e `processed/`) para alimentar o Streamlit              | Michael Dambock   | Em andamento               |
| Executar rotinas automáticas de coleta para diversificar os assuntos no _bucket_                        | Rodrigo           | Ao longo do dia            |
| Estruturar um painel administrativo no Streamlit (visão do volume de arquivos por estágio)              | Michael e Ricieri | Em análise                 |
| Compartilhar referências sobre DuckDB (DuckPad, Wasm/browser) no canal da equipe                        | Michael Dambock   | A realizar                 |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 13 de Novembro de 2026 (Sexta-feira)

- **Horário:** 19h30
