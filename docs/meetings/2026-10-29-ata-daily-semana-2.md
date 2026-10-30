# 📝 Ata de Reunião — Daily (Semana 2)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 29 de Outubro de 2026 (Quinta-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou uma reunião de alinhamento diário em **29/10/2026** para acompanhar a conclusão das tarefas da Semana 1 e o avanço no planejamento da Semana 2. Nos aspectos técnicos, **Vitor** destacou o andamento da revisão da PR S1-09 (interface em Streamlit desenvolvida por Ricieri), identificando uma falha de versionamento no Git provocada pelo nome da pasta `/setup/build` (que foi filtrada pela regra `build` do `.gitignore`). **Rodrigo** relatou a finalização da tarefa S1-11 (coleta de dados do Mastodon via duas APIs públicas, garantindo um volume combinado de 80 itens) e o início dos fluxos da tarefa S2-01. **Michael** confirmou a aplicação de melhorias no arquivo `config.py` e mencionou a liberação da versão 2.0 do DuckDB. Além disso, o grupo decidiu redirecionar os arquivos brutos gerados pelas integrações no n8n para a pasta `raw` (em vez de `samples`), visando o processamento direto no DuckDB, e combinou incluir avisos no documento de credenciais do n8n para lembrar da historização e versionamento futuro dos dados.

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Concluiu a revisão da PR de _fixtures_ do Michael e avançou na revisão da PR S1-09 (Streamlit de Ricieri), sinalizando a necessidade de alterar o nome da pasta `.setup/build` no Docker devido ao bloqueio da regra `build` no `.gitignore`.

- **Para amanhã/Próximos passos:** Finalizar a revisão da PR S1-09, aplicar os ajustes necessários e publicar as PRs pendentes do Gustavo, e organizar a transição das tarefas para a Semana 2.

#### **Rodrigo Aguiar**

- **Feito hoje:** Concluiu o desenvolvimento da tarefa S111, configurando a coleta de dados do Mastodon a partir de duas APIs públicas (assegurando um retorno mínimo de 40 itens por API e 80 itens no total). Deu início aos desenhos de fluxo para a tarefa S2-01.

- **Para amanhã / Próximos passos:** Esclarecer e tratar a pendência relativa ao campo de texto e revisar a PR solicitada por Vitor.

#### **Michael Dambock**

- **Feito hoje:** Revisou as _fixtures_ (S1 e S2) entregues a Vitor e acompanhou o alinhamento sobre a transferência dos arquivos brutos para a pasta `raw`.

- **Para amanhã / Próximos passos:** Implementar os ajustes solicitados no `config.py` e estudar as atualizações da recém-lançada versão 2.0 do DuckDB para otimização da leitura de JSONs.

#### **Ricieri Rosa**

- **Feito hoje:** Teve instabilidades de áudio e conexão durante a chamada, impedindo sua participação ativa nas falas da gravação.

- **Para amanhã / Próximos passos:** Renomear a pasta `/setup/build` do container Docker para evitar o bloqueio no `.gitignore` e acompanhar o término da revisão da PR S1-09.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                                   | Responsável      | Prazo / Status |
| :------------------------------------------------------------------------------------- | :--------------- | :------------- |
| Renomear a pasta `/setup/build` no Docker para evitar o filtro do `.gitignore`         | Ricieri          | A realizar     |
| Finalizar a revisão da PR S1-09 (Streamlit) e publicar os ajustes das PRs do Gustavo   | Vitor            | Em andamento   |
| Subir o PR da tarefa S1-11 (Mastodon com 80 itens) e atualizar a documentação do n8n   | Rodrigo          | Em andamento   |
| Alterar o destino dos arquivos brutos gerados do _bucket_ para a pasta `raw`           | Rodrigo / Equipe | Definido       |
| Incluir aviso no arquivo `n8n-credentials` referente ao versionamento futuro dos dados | Rodrigo          | Em andamento   |
| Implementar ajustes no `config.py` e analisar as novidades do DuckDB 2.0               | Michael          | Em andamento   |


---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 30 de Outubro de 2026 (Sexta-feira)

- **Horário:** 19h30
