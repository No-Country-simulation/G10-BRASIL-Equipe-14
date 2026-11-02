# 📝 Ata de Reunião — Daily (Semana 2)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 30 de Outubro de 2026 (Sexta-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou a reunião diária (_daily_) de acompanhamento em **30/10/2026** para alinhar o encerramento das pendências da Semana 1 e o avanço nas tarefas da Semana 2. **Vitor** concluiu a revisão das PRs S1-03, S1-04, S1-09 e S1-11, comprometendo-se a aplicar e testar os ajustes durante o final de semana. **Rodrigo** finalizou o webhook do Mastodon (S1-11) e iniciou os testes da tarefa S2-01, conectando a leitura de dados do _bucket_ (Mastodon, Stack Overflow e Hacker News) a modelos de linguagem (LLM); ele apresentou uma proposta de _schema_ JSON de saída para classificação de sentimentos e ficou responsável por criar uma tabela comparativa de provedores/modelos gratuitos (OpenRouter, NVIDIA, Groq). **Michael** assumiu a tarefa S2-04 para desenvolver a integração de conexão com a Oracle Cloud Infrastructure (OCI) e comprometeu-se a realizar o _commit_ dos arquivos de configuração pendentes da tarefa S1-02. Por fim, o grupo alinhou manter o fluxo de trabalho durante o final de semana e agendou a próxima reunião para a segunda-feira (feriado) em horário flexível.

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Concluiu a revisão das Pull Requests pendentes no repositório S1-03, S1-04, S1-09 e S1-11 (referentes às entregas do Gustavo, Ricieri e Rodrigo). Sugeriu o uso das APIs gratuitas multimodais da NVIDIA (como Nemotron, Qwen, Mistral).

- **Para amanhã/Próximos passos:**  Testar e aplicar os ajustes das PRs S1-03 e S1-04 durante o final de semana (prevendo envio até o dia seguinte), revisar o _schema_ JSON de saída proposto pelo Rodrigo para avaliação do LLM e validar os ajustes que o Ricieri enviar.

#### **Ricieri Rosa**

- **Feito hoje:** Concluindo os ajustes solicitados na revisão da PR S1-09.

- **Para amanhã / Próximos passos:** Concluir a revisão e dar continuidade à PR S2-03.

#### **Rodrigo Aguiar**

- **Feito hoje:** Concluiu as alterações solicitadas na interface em Streamlit para deixá-la mais enxuta. Finalizou a tarefa S1-11 (Webhook/Mastodon via APIs públicas com limite de 40 itens por requisição) e priorizou a tarefa S2-01, consumindo arquivos brutos diretamente do _bucket_ (80 itens do Mastodon, 151 itens do Stack Overflow e Hacker News). Apresentou a proposta do _schema_ JSON de saída para a avaliação do LLM (contendo pontuações positiva/neutra/negativa, fonte, sentimento final e ID do post).

- **Para amanhã / Próximos passos:** Criar uma planilha comparativa no Excel analisando limites de requisição, janelas de contexto e cotas gratuitas entre provedores de LLM (OpenRouter, NVIDIA, Groq) para apresentação na reunião de segunda-feira.

#### **Michael Dambock**

- **Feito hoje:** Assumiu a tarefa S2-04 para construir o módulo de conexão com a Oracle Cloud Infrastructure (OCI).

- **Para amanhã / Próximos passos:** Fazer o _commit_ das configurações pendentes (`source_config`, `config.yml`) referentes à tarefa S1-02 (dados sintéticos) e avançar no desenvolvimento do conector com a OCI.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                                   | Responsável     | Prazo / Status                 |
| :------------------------------------------------------------------------------------- | :-------------- | :----------------------------- |
| Aplicar e testar os ajustes das APIs (Gustavo e Vinícius)                              | Vitor           | Final de semana / Em andamento |
| Concluir os ajustes da revisão da PR S1-09 e dar continuidade à PR S2-03               | Ricieri          | Em andamento                   |
| Realizar o commit das configurações pendentes da tarefa S1-02 (`src.config`)        | Michael          | Em andamento                   |
| Desenvolver o módulo de conexão com a OCI (S2-04)                                      | Michael          | Em andamento                   |
| Elaborar planilha comparativa de modelos de LLM gratuitos (OpenRouter, NVIDIA, Groq)   | Rodrigo         | Até segunda-feira              |
| Validar o schema JSON de saída da avaliação do LLM                                     | Vitor e Rodrigo | Em andamento                   |
| Realizar reunião diária/Sprint Planning na segunda-feira (feriado) em horário flexível | Toda a equipe   | Agendado para segunda-feira    |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Sprint Planning (Início da Semana 3)

- **Data:** 02 de Novembro de 2026 (Segunda-feira)

- **Horário:** 19h30
