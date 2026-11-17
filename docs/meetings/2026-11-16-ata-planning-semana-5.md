# 📝 Ata de Reunião — Sprint Planning / Daily (Semana 5)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 16 de Novembro de 2026 (Segunda-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhamento das atividades iniciais do projeto na **Semana 5**, que será focado na Documentação e Revisão Final do projeto. Além disso, foi realizada a daily para alinhar as atividades realizadas ao longo do dia e final de semana, atividades previstas, impedimentos e dificuldades encontradas. 

---

## 2. Resumo Executivo

A equipe realizou a sua reunião diária (_daily_) em **16/11/2026** para alinhar os ajustes finais do desenvolvimento, padronizar a identidade visual das telas, organizar as obrigações administrativas e planejar as entregas para a semana final do Hackathon (com prazo de submissão no domingo, 22/11, e _Demo Day_ na terça-feira, 24/11). **Rodrigo** apresentou a conclusão da tarefa **S3-06**, incluindo a tela de análise de sentimentos e tópicos (com _treemap_ configurável), a integração de um _chatbot_ consumindo o DuckDB e a documentação atualizada em `docs/specs`. **Rodrigo** e **Vitor** realizaram o _merge_ (_Squash and merge_) dos PRs das tarefas **S2-01** e **S2-02** no GitHub, fechando automaticamente as _issues_ correspondentes no Kanban.

Em termos de decisões de escopo e gestão, a equipe aprovou o arquivamento da tarefa **S3-01** (integração automatizada de postagens no LinkedIn), classificando-a como recurso opcional para evitar dispersão de foco na reta final. Decidiu-se também atualizar o arquivo `README.md` para manter apenas os nomes dos integrantes ativos. Por fim, alinhou-se a estratégia para o preenchimento da **Avaliação 360° obrigatória**: Everton Santos e Davi Lima serão marcados como ausentes por não terem participado do projeto, enquanto Gustavo Silva receberá pontuação proporcional aos entregáveis das duas tarefas iniciais.

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Rodrigo Aguiar**

- **Feito hoje:** Concluiu as implementações e documentação da tarefa **S3-06** (páginas de sentimentos e tópicos, _treemap_ interativo, _chatbot_ integrado ao DuckDB e documentação técnica em `docs/specs`). Atualizou o _template_ visual das páginas com base na paleta e logotipo criados por Vitor e ajustou os comentários da PR **S2-01**.

- **Para amanhã / Próximos passos:** Revisar as _issues_ pendentes em modo de _review_.

#### **Michael Dambock**

- **Feito hoje:** Apresentou o protótipo de interface e levantou esclarecimentos técnicos sobre o fluxo de dados entre o _bucket_ da OCI, os arquivos JSON e a camada do DuckDB no Streamlit. Destacou o desempenho da equipe no painel de acompanhamento do Hackathon (3º lugar individual e 3 membros no Top 10).

- **Para amanhã / Próximos passos:** Adaptar o layout da tela de curadoria (tarefa **S3-04**) à nova identidade visual e padronização de cores da **S3-06**, finalizando a integração dos arquivos JSON com o DuckDB.

#### **Vitor Pires**

- **Feito hoje:** Criou a paleta de cores e logotipo do projeto, aprovou e revisou os PRs das tarefas **S2-01** e **S2-02**.

- **Para amanhã/Próximos passos:** Revisar e aprovar os Pull Requests das tarefas **S3-02**, **S3-03** e **S3-06**, e atualizar a imagem do diagrama de arquitetura no repositório e remover os nomes de integrantes inativos do `README.md`.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                                  | Responsável     | Prazo / Status         |
| :------------------------------------------------------------------------------------ | :-------------- | :--------------------- |
| Revisar e aprovar as PRs das _issues_ **S3-02**, **S3-03** e **S3-06**                | Vitor           | Prioritário / Imediato |
| Adaptar a tela de curadoria (**S304**) à nova identidade visual da **S3-06**          | Michael         | Em andamento           |
| Limpar nomes de membros inativos no `README.md` e atualizar o diagrama de arquitetura | Vitor           | Esta semana            |
| Alinhar e preencher a Avaliação 360° obrigatória na plataforma                        | Toda a equipe   | Até 22/11 (Domingo)    |
| Gravar o vídeo demonstrativo do projeto (máximo de 5 minutos)                         | Toda a equipe   | Até 22/11 (Domingo)    |
| Ensaio do _pitch_ e preparação para o _Demo Day_                                      | Toda a equipe   | 24/11 (Terça-feira)    |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 17 de Novembro de 2026 (Terça-feira)

- **Horário:** 20h00
