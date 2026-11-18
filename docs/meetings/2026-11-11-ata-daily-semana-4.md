# 📝 Ata de Reunião — Daily (Semana 4)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 11 de Novembro de 2026 (Quarta-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou a sua reunião diária (_daily_) em **11/11/2026** para alinhar a readequação dos fluxos no n8n, a arquitetura dos agentes de geração de conteúdo e o papel da curadoria humana na entrega final. **Rodrigo** concluiu a reestruturação dos três _workflows_ principais (tarefas **S2-01** e **S3-03**), adaptando-os para suportar múltiplos tópicos/tags Docker e disponibilizando o Webhook WF12 para integração com o Streamlit. No âmbito da arquitetura de inteligência artificial, o grupo concordou em criar **agentes especialistas dedicados** para cada canal/editorial (LinkedIn, Newsletter e FAQ) em vez de centralizar a geração em uma única IA. Ficou rigorosamente estabelecido que o **painel de curadoria funcionará como um filtro humano obrigatório** (_human-in-the-loop_), descartando a postagem 100% automatizada. Como propostas de valor e demonstração prática para a entrega, a equipe levantou a integração de alertas por WhatsApp para notificar a equipe sobre novos conteúdos pendentes de revisão, a publicação de testes reais no LinkedIn/Instagram citando o programa (GDEs/Oracle) e o rastreamento de acessos via Google Analytics. Por fim, **Michael** e **Vitor** trabalharam na resolução de conflitos de _merge_ no arquivo `config.py` e no ajuste da tarefa **S2-04**, utilizando a funcionalidade nativa de _retry_ do SDK da OCI para prevenir loops infinitos em caso de erro.

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Rodrigo Aguiar**

- **Feito hoje:** Readequou os três fluxos de trabalho no n8n para garantir compatibilidade com diferentes tags Docker e parâmetros de busca por plataforma. Entregou a tarefa **S2-01** com especificações atualizadas em `docs/specs` e disponibilizou a tarefa **S3-03** (Webhook WF12 para consumo do Streamlit). Propos a criação de agentes de IA dedicados e especialistas para cada tipo de saída (LinkedIn, Newsletter, FAQ) utilizando as pastas já categorizadas no _bucket_.

- **Para amanhã / Próximos passos:** Ajustar a resposta do Webhook WF12 para que o payload retornado esteja 100% alinhado ao `input_schema` esperado pela interface Streamlit de Ricieri.

#### **Vitor Pires**

- **Feito hoje:** Acompanhou o _merge_ da PR da interface do Ricieri (**S2-03**) na branch `develop`. Trabalhou na resolução de conflitos de _merge_ nas tarefas **S1-04** e **S1-05** decorrentes de alterações no arquivo `config.py`. Colocou a PR da tarefa **S3-03** em estado de revisão (_review_).

- **Para amanhã/Próximos passos:** Finalizar a resolução dos conflitos das tarefas **S1-04** e **S1-05**, revisar a **PR S3-03** de Rodrigo e organizar com o grupo o escopo do painel de curadoria humana (tarefas **S3-01**/**S3-04**).

#### **Michael Dambock**

- **Feito hoje:** Trabalhou nos ajustes da tarefa **S2-04** (integração OCI), substituindo o bloco de tratamento genérico `try...except` pela rotina de _retry_ nativa do próprio SDK da OCI para evitar requisições infinitas em malha de erro. Transicionou o Pull Request da tarefa **S3-05** de _draft_ para versão final de revisão.

- **Para amanhã / Próximos passos:** Resolver os conflitos de _merge_ pendentes no arquivo `config.py` e homologar o fechamento da tarefa S2-04.

#### **Ricieri Rosa**

- **Feito hoje:** Teve o Pull Request da tarefa **S2-03** integrado com sucesso à branch `develop`. Deu início à integração da interface Streamlit com o Webhook de consumo (tarefa **S3-03** / WF12), alinhando com Rodrigo o formato do JSON esperado.

- **Para amanhã / Próximos passos:** Conectar as telas do Streamlit ao Webhook WF12 assim que a estrutura do `input_schema` for ajustada por Rodrigo.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                                                                                                                     | Responsável       | Prazo / Status                       |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- | :----------------------------------- |
| Ajustar a estrutura de retorno do Webhook WF12 (S3-03) conforme o `input_schema` do Streamlit                                                                             | Rodrigo e Ricieri | Prioritário / Em andamento           |
| Resolver conflitos de _merge_ no arquivo `config.py` para as PRs S1-04, S1-05 e S2-04                                                                                       | Vitor e Michael   | Em andamento                         |
| Estruturar sub-workflows com agentes especialistas dedicados por tipo de conteúdo (FAQ, Newsletter, LinkedIn)                                                            | Rodrigo           | Em andamento                         |
| Manter a etapa de curadoria humana como filtro obrigatório antes de qualquer publicação                                                                                  | Toda a equipe     | Definido                             |
| Validar propostas de engajamento para a demo final (alertas por WhatsApp, postagens reais no LinkedIn/Instagram marcando o programa e rastreamento via Google Analytics) | Rodrigo e Equipe  | Em análise / A consultar com suporte |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 12 de Novembro de 2026 (Quinta-feira)

- **Horário:** 19h30
