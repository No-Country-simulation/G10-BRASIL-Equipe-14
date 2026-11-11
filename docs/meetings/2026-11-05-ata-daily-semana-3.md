# 📝 Ata de Reunião — Daily (Semana 3)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 05 de Novembro de 2026 (Quinta-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou a sua reunião diária (_daily_) em **05/11/2026** para acompanhar a integração de fluxos no n8n, a resolução de problemas de acesso à nuvem e a revisão de Pull Requests (PRs). No aspecto de infraestrutura, **Michael** relatou uma falha de visualização no console web da Oracle Cloud Infrastructure (OCI) que exibia o erro _"Could not load data"_ no _namespace_ do Object Storage, embora as requisições via terminal e Python SDK funcionassem normalmente; **Rodrigo** auxiliou verificando as políticas de permissão do grupo. No desenvolvimento de fluxos do n8n, **Rodrigo** avançou na unificação das tarefas **S1-03**, **S1-04** e **S1-05** com a **S2-02**, criando uma estrutura de roteamento (_switch_) com múltiplos agentes de IA (análise de sentimentos, classificação, FAQ e envio para saneamento/revisão humana na OCI). Além disso, a equipe concordou em manter rigorosamente o plano _Always Free_ da OCI (rejeitando a migração para o período de teste expandido de 30 dias) e ajustar os _timestamps_ dos arquivos para microssegundos para evitar colisões no armazenamento.


---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Enviou _commits_ para a tarefa S1-04 com os _prompts_ segmentados e adicionou os _adapters_ do N8N para Discord e Blog. Assumiu a tarefa S2-05 ("Mapear fluxo de execução").

- **Para amanhã/Próximos passos:** Concluir a refatoração das tarefas S1-03, S1-04 e S1-05, revisar o PR aberto por Ricieri e elaborar a documentação do mapa de execução (S2-05) assim que os PRs das tarefas S2-01 e S2-02 forem integrados ao _develop_.

#### **Rodrigo Aguiar**

- **Feito hoje:** Unificou as demandas das tarefas S1-03, S1-04 e S1-05 com a **S2-02** no n8n, criando o nó de roteamento (_switch_) que integra agentes de análise de sentimentos, FAQ, newsletter e redes sociais. Estruturou o fluxo para direcionar os arquivos avaliados para a pasta de saneamento (_human review_) na OCI. Analisou as políticas de acesso do grupo no console da OCI para resolver o bloqueio de exibição enfrentado por Michael.

- **Para amanhã / Próximos passos:** Finalizar a padronização dos parâmetros de requisição para as três fontes de dados (Mastodon, Hacker News e Stack Overflow) e validar o perfil de permissões da conta de Michael na OCI.

#### **Michael Dambock**

- **Feito hoje:** Diagnosticou a falha de exibição de dados no console web da OCI (o _namespace_ fica em branco, enquanto a API/SDK em Python funciona sem problemas). Avançou na finalização da PR da tarefa **S2-04** (persistência na OCI), realizando a remoção da variável obsoleta `fixtures_directory`, ajustando o campo `semana` para `week` no _schema_ `output_json` e configurando os _timestamps_ com microssegundos para evitar conflitos de gravação no mesmo segundo.

- **Para amanhã / Próximos passos:** Concluir a descrição e os comentários do PR da tarefa **S2-04** para submeter à revisão final de Vitor e verificar com o Rodrigo a validação de permissões no console da OCI.

#### **Ricieri Rosa**

- **Feito hoje:** Abriu Pull Request com melhorias na interface e alinhou pendências relativas às telas de entrada de dados.

- **Para amanhã / Próximos passos:** Revisar os itens pendentes da área de Data Science e esclarecer no n8n a identificação da origem das fontes de dados nas telas de entrada.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                               | Responsável      | Prazo / Status    |
| :--------------------------------------------------------------------------------- | :--------------- | :---------------- |
| Ajustar permissões/policies do usuário no console web da OCI                       | Rodrigo e Michael| Em andamento      |
| Submeter PR da tarefa S2-04 (persistência OCI) com timestamps em microssegundos    | Michael          | Em andamento      |
| Concluir os workflows de roteamento/switch (S2-02) unificando S1-03, S1-04 e S1-05 | Rodrigo          | Em andamento      |
| Revisar a PR do Nercio e finalizar a refatoração dos prompts no n8n                | Vitor            | Próximos passos   |
| Elaborar o mapeamento do fluxo de execução (S2-05) pós-merge da S2-01 e S2-02      | Vitor            | Aguardando merges |
| Manter o plano "Always Free" na OCI e realizar limpeza dos arquivos de teste       | Toda a equipe    | Definido          |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 06 de Novembro de 2026 (Sexta-feira)

- **Horário:** 19h30
