# 📝 Ata de Reunião — Daily (Semana 4)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 10 de Novembro de 2026 (Terça-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou uma reunião diária em **10/11/2026** dedicada à revisão das Pull Requests (PRs), padronização de estruturas de dados e refinamento da estratégia para o _Demo Day_. Durante o alinhamento de desenvolvimento, confirmou-se a inclusão do Mastodon no `output_schema.json`, a conclusão da geração de arquivos processados no _processor_ para HackerNews, Mastodon e StackOverflow (abrangendo tópicos como _Artificial Intelligence_ e _Docker_), e a consolidação das métricas de consumo de tokens (média entre 3.000 e 5.000 tokens por requisição). O time também esclareceu divergências na nomenclatura de caminhos dos arquivos JSON (uso de _timestamp_ vs. padrão ISO `Wxx`), definindo que o validador checa apenas a tipagem de dados mas mantendo a busca por padronização. Na preparação da apresentação final, alinhou-se a divisão do tempo em 5 minutos (2 minutos de apresentação teórica/conceitual e 3 minutos de demonstração _live demo_), ajustando a comunicação para focar no valor de negócio e ROI para diretores executivos, além de discutir a proposta de identidade visual e o subtítulo do projeto.


---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Atualizou a PR S1-01 com a inclusão do Mastodon no `output_schema.json` e registrou as métricas de tokens por requisição. Finalizou os ajustes nas PRs S1-04 e S1-05 e revisou a PR S2-03 de interface. Clarificou o funcionamento da validação automática quanto aos caminhos de arquivos.

- **Para amanhã/Próximos passos:** Encerrar os ajustes das PRs S1-04 e S1-05 e aprovar os _commits_ pendentes.

#### **Rodrigo Aguiar**

- **Feito hoje:** Concluiu o arquivo completo na pasta _processor_ para o HackerNews (com objetos de comentários e classificações de sentimento, força e confiança) e finalizou o fluxo principal WF11, iniciando a replicação de roteamento para as demais fontes e adicionando o tópico _Docker_ para comparação com _Artificial Intelligence_.

- **Para amanhã / Próximos passos:** Finalizar os roteamentos do fluxo WF11 no n8n para as demais fontes e acompanhar os testes de carga.

#### **Michael Dambock**

- **Feito hoje:** Questionou a padronização das estruturas de caminho dos JSONs (`config.py` vs `output_schema.json`). Apresentou o roteiro para a apresentação final de 5 minutos focado em valor de negócio, ROI e público executivo, sugerindo a divisão de papéis e a simbologia para a marca do projeto (ex.: _Let Growth_ / _Community Lab_ e a referência a Hermes).

- **Para amanhã / Próximos passos:** Refinar o roteiro dos slides e alinhar a estrutura do pitch de 5 minutos com a equipe.

#### **Ricieri Rosa**

- **Feito hoje:** Concluiu as correções de código e UX solicitadas na revisão da PR S2-03.

- **Para amanhã / Próximos passos:** Aguardando a aprovação para iniciar a próxima issue.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                                     | Responsável     | Prazo / Status |
| :--------------------------------------------------------------------------------------- | :-------------- | :------------- |
| Finalizar os roteamentos do fluxo WF11 no n8n para as demais fontes                      | Rodrigo         | Em andamento   |
| Encerrar os ajustes pendentes da Semana 2 no board Kanban                                | Vitor e Rodrigo | Em andamento   |
| Elaborar a estrutura de slides e o roteiro cronometrado para a apresentação de 5 minutos | Michael e Equipe| Em andamento   |
| Refinar a identidade visual, subtítulo e documentação de UX/UI para a entrega            | Equipe          | A realizar     |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 11 de Novembro de 2026 (Quarta-feira)

- **Horário:** 19h30
