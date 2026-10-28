# 📝 Ata de Reunião — Daily (Semana 2)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 27 de Outubro de 2026 (Terça-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou a sua reunião diária (_daily_) de acompanhamento do projeto em 27/10/2026. Entre os principais pontos discutidos, destacam-se a disponibilização de um script em Python para ingestão de amostras do dataset (**Issue 7 - Semana 1**), a identificação de limitações na API do Mastodon quanto à ausência de filtros por data (diferente do Hacker News e Stack Exchange), a conclusão e abertura de PR do workflow do Hacker News (**Issue 12 - Semana 1**), a definição da obrigatoriedade do parâmetro `query` para evitar sobrecarga de dados e o início da implementação dos nós de triagem com LLM no n8n (**Issue 1 - Semana 2**) utilizando as APIs do Groq e OpenRouter. Foi relatado também um bloqueio temporário na integração do Mastodon (**Issue 11 - Semana 1**) por pendência na validação do e-mail da conta, além da fila de revisões de PRs (prompts e fluxos) e a atualização da especificação de mapeamento de fontes para a versão v3 no repositório.

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Subiu o Pull Request (PR) contendo o script em Python para ingestão de amostras (_samples_) do pacote de dados da **Issue 7 (Semana 1)**, acompanhado de um documento de especificação (_spec_) com os parâmetros das APIs do Mastodon, Hacker News e Stack Exchange. Identificou que o Mastodon não suporta filtro por data (retornando apenas mensagens recentes). Iniciou a revisão das duas PRs enviadas pelo Gustavo (referentes a três _issues_ de _prompts_).

- **Para amanhã/Próximos passos:** Finalizar a revisão das PRs do Gustavo e, em seguida, revisar as PRs do Rodrigo e do Ricieri. Enviar as atas registradas (daily anterior e a de hoje) e atualizar a documentação de mapeamento de fontes e campos para a versão v3 no repositório.

#### **Rodrigo Aguiar**

- **Feito hoje:** Concluiu o _workflow_ do Hacker News (**Issue 12 - Semana 1**) e abriu o respectivo PR, deixando o _webhook_ ativo (destacando a diferença entre os _endpoints_ de produção e teste `webhook-test`). Definiu o parâmetro `query` como obrigatório na requisição do Hacker News para limitar o volume de dados trazidos. Iniciou a **Issue 1 da Semana 2**, configurando os nós de triagem de LLM no n8n com chaves de API da Groq e da OpenRouter para preparar a estrutura de testes dos _prompts_.

- **Para amanhã / Próximos passos:** Acompanhar a validação do e-mail de confirmação da conta do Mastodon para desbloquear a **Issue 11 (Semana 1)**, prosseguir com o desenvolvimento da automação no n8n para a Semana 2 e enviar o PR correspondente.

#### **Ricieri Rosa**

- **Feito hoje:** Puxou a nova tarefa em sua _branch_ de trabalho, mantendo cautela no desenvolvimento para facilitar um posterior _rebase_ ou _merge_ em relação às alterações paralelas de outros membros da equipe.

- **Para amanhã / Próximos passos:** Esclarecer dúvidas pontuais sobre a tarefa no canal oficial do grupo e dar sequência ao código assim que a sua PR anterior for revisada por Vítor.

#### **Michael Dambock**

- **Feito hoje:** Não conseguiu produzir hoje.

- **Para amanhã / Próximos passos:** Dar continuidade à task S1-02.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                                           | Responsável | Prazo / Status        |
| :--------------------------------------------------------------------------------------------- | :---------- | :-------------------- |
| Revisar as PRs pendentes do Gustavo (_prompts_), Rodrigo (Hacker News) e Riciery               | Vitor       | Em andamento          |
| Enviar as atas completas das reuniões diárias (ontem e hoje)                                   | Vitor       | Em andamento          |
| Atualizar o documento de mapeamento de fontes/campos (`mapeamento_fontes.md`) com o comparativo dos campos das fontes de dados na versão v3 | Vitor       | Previsto / A realizar |
| Aguardar e-mail de confirmação de conta do Mastodon para desbloqueio da Issue 11               | Rodrigo     | Aguardando e-mail     |
| Desenvolver e estruturar os nós de triagem de LLM no n8n (Groq/OpenRouter) para a Semana 2     | Rodrigo     | Em andamento          |
| Publicar dúvidas técnicas sobre a nova tarefa no canal do Discord                              | Ricieri     | A realizar            |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 28 de Outubro de 2026 (Quarta-feira)

- **Horário:** 19h30
