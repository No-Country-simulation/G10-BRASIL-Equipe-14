# 📝 Ata de Reunião — Daily (Semana 2)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 28 de Outubro de 2026 (Quarta-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou uma reunião diária (_daily_) de acompanhamento em **28/10/2026** para alinhar revisões de código, documentações de APIs e a estratégia de versionamento dos dados. No aspecto de desenvolvimento, foram concluídas as revisões das tarefas S1-06, S1-12 (Rodrigo) e do dataset de ruído (Michel), estando em andamento a revisão da tarefa S1-09 (Ricieri). Vitor assumiu o compromisso de aplicar os ajustes necessários e publicar as Pull Requests (PRs) de _prompts_ do Gustavo devido à sua ausência prolongada. Também foram implementados o formulário de upload de dados de entrada com validação por _schema_ e adicionadas as especificações de credenciais do n8n e comunidades da API do Stack Exchange em `docs/specs`. A equipe decidiu que, para o período atual de testes, os arquivos de amostras podem continuar sendo sobrescritos no _bucket_, mas adotará futuramente a inclusão de _timestamps_ nos nomes para criar histórico sem comprometer o limite de armazenamento. Por fim, alinhou-se a limitação da API do Mastodon (que ignora parâmetros de busca por data) e liberou-se o acesso a uma instância pública para dar continuidade aos testes do fluxo.

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Concluiu a revisão das PRs S1-06 e S1-12 do Rodrigo e da PR S1-02 do Michael. Iniciou a revisão da PR S1-09 do Ricieri.

- **Para amanhã/Próximos passos:** Terminar a revisão da PR S1-09 e assumir os ajustes e a publicação das PRs de _prompts_ do Gustavo para evitar atrasos na entrega. Atualizar a documentação da API do Mastodon (`docs/specs`) registrando que a filtragem por data é ignorada pela plataforma, além de disponibilizar a URL da instância pública para testes da equipe.

#### **Ricieri Rosa**

- **Feito hoje:** Desenvolveu a inclusão do formulário para upload dos dados de entrada na interface da aplicação e implementou a validação por _schema_ dos dados.

- **Para amanhã / Próximos passos:** Esclarecer e tratar a pendência relativa ao campo de texto e revisar a PR solicitada por Vitor.

#### **Rodrigo Aguiar**

- **Feito hoje:** Finalizou a revisão da Issue #6 (Stack Exchange) no _develop_ e publicou a documentação técnica na pasta `docs/specs`, incluindo os parâmetros da API do Stack Exchange e as credenciais/URLs ativas dos _workflows_ do n8n. Mapeou os 5 principais sites da rede Stack Exchange com maior volume diário de perguntas (Stack Overflow, Math, Ask Ubuntu, Physics, etc.) para propor a diversificação de temas no projeto.

- **Para amanhã / Próximos passos:** Utilizar a instância pública do Mastodon fornecida por Vitor para testar a requisição HTTP no n8n enquanto aguarda o e-mail de aprovação da conta oficial.

#### **Michael Dambock**

- **Feito hoje:**  Conduziu a discussão sobre a necessidade de versionar ou sobrescrever os arquivos de amostras (_samples_) no _bucket_, confirmando a manutenção dos dados sintéticos na pasta `data/fixtures` (Issue S1-07) com sete pontos levantados para revisão.

- **Para amanhã / Próximos passos:** Acompanhar as discussões dos pontos levantados no Discord e auxiliar nos ajustes das transcrições e do _system prompt_.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                                                    | Responsável            | Prazo / Status              |
| :------------------------------------------------------------------------------------------------------ | :--------------------- | :-------------------------- |
| Finalizar a revisão da PR S1-09 (Ricieri) e ajustar/subir as PRs de _prompts_ do Gustavo                | Vitor                  | Em andamento                |
| Atualizar a especificação em `docs/specs` documentando a limitação de data da API do Mastodon           | Vitor                  | Previsto                    |
| Esclarecer a dúvida técnica sobre o campo de texto e revisar a PR S1-0 9                                | Ricieri                | Em andamento                |
| Testar os fluxos HTTP do Mastodon via n8n utilizando a instância pública pública compartilhada          | Michel                 | Em andamento                |
| Avaliar a expansão das buscas para outras comunidades da API do Stack Exchange                          | Toda a equipe          | Em análise                  |
| Incluir _timestamps_ na nomenclatura de arquivos de _samples_ quando houver necessidade de historização | Rodrigo e Equipe       | A definir para a fase final |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 29 de Outubro de 2026 (Quinta-feira)

- **Horário:** 19h30
