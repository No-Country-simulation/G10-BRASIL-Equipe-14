# 📝 Ata de Reunião — Daily / Alinhamento Geral (Semana 3)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 04 de Novembro de 2026 (Quarta-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A reunião diária de **04/11/2026** focou no alinhamento e limpeza do _backlog_ de Pull Requests (PRs) pendentes das Semanas 1 e 2 para impedir o acúmulo de tarefas antes de iniciar as demandas da Semana 3. No âmbito técnico, consolidaram-se as entregas da tarefa **S1-02** (ajustes no `config.py` por **Michael**) e da **S1-03** (refatoração e modularização dos prompts por **Vitor**, separando o código monolítico e adicionando 5 casos de teste reais para cada uma das três fontes: Stack Exchange, Mastodon e Hacker News). **Rodrigo** apresentou o progresso da tarefa **S2-01**, onde o agente de IA no n8n foi configurado com um mecanismo de _fallback_ entre dois provedores (OpenRouter e NVIDIA), parser de saída padronizado em JSON e persistência na pasta `processed` do bucket da OCI. Em relação à infraestrutura e regras de negócio, aprovou-se manter a gravação com _timestamp_ na OCI sem restrições rígidas de duplicidade/hash para a fase de MVP (**S2-04**), decidiu-se desvincular a execução automática dos _workflows_ de coleta a cada análise do agente para otimizar a performance, e confirmou-se a simplicidade da gravação do vídeo demonstrativo final usando o OBS Studio.


---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Leu a ata da reunião anterior e conduziu o alinhamento focado na revisão do _backlog_ no Kanban. Refatorou a tarefa S1-03, separando os prompts em arquivos utilitários e adicionando 5 casos de teste reais para cada fonte (Stack Exchange, Mastodon e Hacker News). Deixou os ajustes das tarefas S1-04 e S1-05 prontos, aguardando apenas o merge da S1-03.

- **Para amanhã/Próximos passos:** Concluir as revisões e merges das tarefas S1-02 (Michael) e S1-03 (Vitor/Rodrigo) e, em seguida, submeter os PRs das tarefas S1-04 e S1-05 para zerar as pendências da Semana 1.

#### **Rodrigo Aguiar**

- **Feito hoje:** Implementou o _system prompt_ da tarefa S1-03 no agente de IA do n8n para a tarefa S2-01 (Stack Overflow), configurando a redundância entre os provedores OpenRouter e NVIDIA (_fallback_). Estruturou os nós de _skill_, o prompt de sistema e o _output parser_ padronizado em JSON com sentimento, força, confiança e resumo, direcionando a saída para a pasta `processed` do bucket. Concluiu a captura de comentários e estruturas pai/filho da fonte Hacker News.

- **Para amanhã / Próximos passos:** Prosseguir com a construção dos nós condicionais de roteamento na tarefa S2-02 ('In Progress') e manter os _workflows_ de obtenção de dados desvinculados do gatilho automático de análise.

#### **Michael Dambock**

- **Feito hoje:** Finalizou as alterações da tarefa S1-02. Apresentou seis pontos de validação para a tarefa S2-04 (OCI Object Storage), abordando as regras de hash de duplicidade, status pendente antes do upload, prefixo de testes (`tests/`) e padronização do calendário ISO para semanas (`W44`).

- **Para amanhã / Próximos passos:** Concluir a implementação da tarefa S2-04 adotando a regra simplificada de gravação por _timestamp_ no MVP (sem checagem complexa de duplicidade por hash), mantendo uma rotina alternativa de substituição caso seja necessário no futuro.

#### **Ricieri Rosa**

- **Feito hoje:** Retomou o trabalho na tarefa S2-03 (telas de entrada de dados no Streamlit), que estava pausada aguardando o merge da tarefa dependente. Sugeriu a utilização de um parâmetro booleano para controle de reescrita no módulo de storage.

- **Para amanhã / Próximos passos:** Desenvolver e integrar as telas de entrada de dados no Streamlit (S2-03) agora que as dependências da pipeline foram desbloqueadas.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                               | Responsável      | Prazo / Status          |
| :--------------------------------------------------------------------------------- | :--------------- | :---------------------- |
| Realizar review e merge das tarefas S1-02 (Michael) e S1-03 (Vitor)                | Vitor e Rodrigo  | Prioritário / Hoje      |
| Submeter as alterações das tarefas S1-04 e S1-05 pós-merge da S1-03                | Vitor            | Imediato                |
| Avançar no desenvolvimento da tarefa S2-02 (nós condicionais no n8n)               | Rodrigo          | Em andamento            |
| Desenvolver a interface de entrada de dados no Streamlit (S2-03)                   | Ricieri          | Liberado / Em andamento |
| Finalizar a tarefa S2-04 com regras simplificadas de gravação na OCI               | Michael          | Em andamento            |
| Manter a desvinculação entre os fluxos de coleta e a execução do agente de análise | Rodrigo e Equipe | Definido                |
| Planejar a gravação da demonstração em vídeo (MVP) utilizando o OBS Studio         | Toda a equipe    | A realizar              |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 05 de Novembro de 2026 (Quinta-feira)

- **Horário:** 19h30
