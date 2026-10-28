# 📝 Ata de Reunião — Sprint Planning / Daily (Semana 2)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 26 de Outubro de 2026 (Segunda-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhamento das atividades iniciais do projeto na **Semana 2**, que será focado na orquestração condicional no n8n e módulos da interface. Além disso, foi realizada a daily para alinhar as atividades realizadas ao longo do dia, atividades previstas, impedimentos/dificuldades encontradas. 

---

## 2. Resumo Executivo

A equipe realizou uma reunião de planejamento semanal (_Sprint Planning_) e alinhamento diário (_daily sync_) em 26/10/2026 para revisar as entregas do fim de semana e organizar o cronograma da semana. No âmbito técnico, definiu-se a **divisão dos workflows no n8n em requisições separadas** (_Questions_, _Licenses_ e _Answers_) para contornar limitações de memória e garantir que o campo `content_license` não retorne nulo. O **Workflow 05** foi configurado para automatizar o download dos três arquivos zipados diretamente para o ambiente dos desenvolvedores. Além disso, concordou-se em **manter os dados brutos com tags HTML no banco de dados**, adiando a conversão para Markdown para a etapa de consumo pelos modelos de linguagem (LLM). A equipe também alinhou os preparativos para as entregas finais do programa (documentação central no repositório, vídeo de demonstração no YouTube, links e _deploy_) e acompanhou o progresso do _boilerplate_ da interface.

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Subiu amostras de dados do Mastodon e do Hacker News. Explicou a automação do GitHub Projects (reajustando o status da Issue #7 para _In Progress_ para cobrir os itens restantes) e iniciou a revisão das PRs enviadas pelo Gustavo (prompts), Rodrigo (padronizações) e Uissieri (Issue #9).

- **Para amanhã/Próximos passos:** Concluir a revisão das PRs pendentes, assumir a criação e revisão dos _prompts_ caso o Gustavo precise se ausentar do projeto, e estruturar o arquivo central de documentação em Markdown apontando para as pastas de atas e especificações.

#### **Rodrigo Aguiar**

- **Feito hoje:** Separou o fluxo de requisições no n8n em três workflows distintos (WF02 para _Questions_, WF03 para _Licenses_ e WF04 para _Answers_), eliminando sobrecargas e dados nulos de licenças. Desenvolveu o WF05 para permitir o download dos três arquivos zipados via comando no PowerShell (com suporte a parâmetros de _tag_, data, limite de 100 itens e site). Padronizou o nome dos arquivos no repositório e disponibilizou a chave secreta de testes no Discord.

- **Para amanhã / Próximos passos:** Atualizar as alterações dos workflows no repositório (PR da Issue #6) e focar na construção e liberação rápida dos fluxos para coleta de dados do Hacker News e do Mastodon.

#### **Michael Dambock**

- **Feito hoje:** Testou o download dos arquivos zipados do n8n, confirmando a integridade dos JSONs e a presença do campo `content_license` sem nulos graças ao espaçamento das requisições. Alertou a equipe sobre a necessidade de organizar com antecedência os materiais de entrega final (vídeo demo, repositório e documentação).

- **Para amanhã / Próximos passos:** Dar continuidade ao tratamento e validação dos dados do Mastodon assim que a automação for disponibilizada, aproveitando a correlação por `source_ID`.

#### **Ricieri Rosa**

- **Feito hoje:** Desenvolveu e enviou a PR da Issue #9 contendo a estrutura base do _boilerplate_ da aplicação e o roteamento de páginas no Streamlit.

- **Para amanhã / Próximos passos:** Aguardar a revisão da PR e acompanhar o planejamento das tarefas de interface para a Semana 2.

#### **Gustavo Silva**

- **Feito hoje:** Subiu duas PRs contendo três _issues_ de _prompts_ e informou ao grupo a possibilidade de afastamento por restrições de tempo no trabalho.

- **Para amanhã / Próximos passos:** Acompanhar a revisão dos _prompts_ ou repassar o módulo para a condução do Vitor.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                                             | Responsável      | Prazo / Status                |
| :----------------------------------------------------------------------------------------------- | :--------------- | :---------------------------- |
| Atualizar os workflows do n8n no repositório com amostras do Stack Exchange (PR Issue #6)        | Rodrigo          | Em andamento / Hoje à noite   |
| Priorizar o desenvolvimento dos fluxos de coleta para Hacker News e Mastodon                     | Rodrigo          | Alta prioridade               |
| Concluir a revisão das PRs de _prompts_ (Gustavo) e de _boilerplate_ (Uissieri)                  | Vitor            | Em andamento                  |
| Reajustar a Issue #7 para _In Progress_ no GitHub Projects                                       | Vitor            | Concluído                     |
| Manter o corpo de dados em HTML bruto no banco de dados, convertendo para Markdown apenas no LLM | Rodrigo e Equipe | Definido                      |
| Estruturar a documentação principal em Markdown no repositório apontando para atas e specs       | Vitor            | Próximos passos               |
| Dar sequência à validação e tratamento de dados do Mastodon                                      | Michel           | Aguardando liberação do fluxo |
| Iniciar as tarefas da Semana 2 (nós condicionais do router e integração de LLM no n8n)           | Toda a equipe    | Agendado para a Semana 2      |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 27 de Outubro de 2026 (Terça-feira)

- **Horário:** 19h30
