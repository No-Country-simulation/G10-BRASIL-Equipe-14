# 📝 Ata de Reunião — Sprint Planning / Daily (Semana 4)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 09 de Novembro de 2026 (Segunda-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhamento das atividades iniciais do projeto na **Semana 4**, que será focado em Homologacção, Integração com OCI e Revisão Inicial. Além disso, foi realizada a daily para alinhar as atividades realizadas ao longo do dia e final de semana, atividades previstas, impedimentos e dificuldades encontradas. 

---

## 2. Resumo Executivo

A equipe realizou uma reunião de planejamento semanal (_Sprint Planning_) e alinhamento diário (_daily_) de acompanhamento do projeto em **09/11/2026** onde a equipe avaliou o volume de dados e o consumo de tokens na execução dos modelos de linguagem (Gemini e NVIDIA) via API, além de planejar a apresentação final do projeto. A análise técnica revelou um consumo médio de 4.500 a 5.000 tokens por requisição (atingindo até 10.000 tokens em posts extensos), somando cerca de 80.000 tokens para 17 casos de teste real. Para não estourar as cotas diárias gratuitas dos modelos, o grupo concordou em espaçar as requisições ao longo do dia ao povoar o _bucket_ da OCI. No aspecto do código e repositório, ajustaram-se validações (`try/except`), limitou-se o tamanho de upload no Streamlit para no máximo 10 MB (evitando o limite padrão de 200 MB) e atualizaram-se as documentações das APIs do Mastodon e Stack Exchange. Por fim, organizou-se o formato da apresentação final, estabelecendo um limite rígido de 5 minutos dividido entre pitch executivo e demonstração prática da interface.

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Analisou os resultados de contagem de tokens no router (média de 4.500 tokens por item), ajustou os prompts tornando os exemplos (_few-shots_) opcionais para economizar contexto e atualizou a especificação do router. Definiu o limite de 10 MB para uploads no Streamlit e manteve bloqueada a tarefa S2-05 aguardando a conclusão dos fluxos no n8n.

- **Para amanhã/Próximos passos:** Atualizar os arquivos de especificação em `docs/specs` com as métricas de tokens e finalizar os comandos do repositório na PR.

#### **Rodrigo Aguiar**

- **Feito hoje:** Finalizou o roteamento e classificação de publicações no n8n para Mastodon (50 itens / 21 min) e Stack Exchange (10 itens / 1h 16min / \~56 mil tokens). Atualizou as especificações em `docs/specs` e propôs realizar requisições fracionadas ao longo do dia para popular o _bucket_ com novos tópicos (_Docker_ e _Artificial Intelligence_).

- **Para amanhã / Próximos passos:** Realizar a captura e processamento do Hacker News e manter a carga fracionada de arquivos no _bucket_.

#### **Ricieri Rosa**

- **Feito hoje:** Realizou as correções de código e UX solicitadas na revisão da PR S2-03.

- **Para amanhã / Próximos passos:** Concluir as demais correções de código para iniciar a próxima issue.

#### **Michael Dambock**

- **Feito hoje:** Discutiu os limites de tokens por requisição, apoiou o espaçamento das chamadas para proteção das cotas e sugeriu organizar a apresentação final de 5 minutos dividindo a introdução teórica e a demonstração da interface.

- **Para amanhã / Próximos passos:** Aplicar tratamento com `try/except` na tarefa S204 e testar ferramentas de gravação (OBS Studio, Google Vids, NotebookLM) para a demonstração final.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                        | Responsável     | Prazo / Status              |
| :-------------------------------------------------------------------------- | :-------------- | :-------------------------- |
| Subir a PR refatorada de _prompts_ com _guardrails_ e suporte a Hacker News | Vitor           | Hoje à noite / Em andamento |
| Revisar as três PRs pendentes no repositório                                | Vitor           | Próximos passos             |
| Fixar tópicos e categorias _tech_ predefinidas para a busca no _front-end_  | Rodrigo e Vitor | Definido / A implementar    |
| Implementar nós condicionais de roteamento no n8n (tarefa da Semana 2)      | Rodrigo         | Em andamento                |
| Finalizar revisão de código da PR S2-03                                     | Ricieri         | Em andamento                |
| Finalizar o módulo de conexão com a OCI e integração CI/CD                  | Michael         | Em andamento                |
| Revisar e atualizar os _cards_ no Kanban do GitHub Projects para a Semana 3 | Toda a equipe   | Em andamento                |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 10 de Novembro de 2026 (Terça-feira)

- **Horário:** 19h30
