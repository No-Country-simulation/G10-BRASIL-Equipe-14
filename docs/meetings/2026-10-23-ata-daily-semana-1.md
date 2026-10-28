# 📝 Ata de Reunião — Daily (Semana 1)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 23 de Outubro de 2026 (Sexta-feira, 19h00)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou uma reunião de acompanhamento diário (_daily_) e revisão das entregas semanais do projeto no programa No Country. Ficou acordada a manutenção do horário fixo das reuniões diárias às **19:30**, com atividades assíncronas durante o fim de semana e a realização da reunião de planejamento (_Sprint Planning_) na segunda-feira. No âmbito de desenvolvimento, consolidou-se a padronização de nomenclatura de arquivos e funções (renomeação de `validator.py` para `schema_validator.py` e da função para `validate_data`), a criação de registros de decisão arquitetural (ADRs para o JSON Schema e versão fixa do n8n) e a centralização de diretórios no `config.py`. Além disso, concluiu-se a validação do primeiro cenário real na branch `dataset_scenarios`, definiu-se a separação e duplicação dos _workflows_ na OCI/n8n para cada fonte de dados (**Stack Exchange, Hacker News e Mastodon**) para facilitar futuras manutenções, e confirmou-se a containerização da aplicação Streamlit em **Docker**.

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Ajustou as transcrições das _dailies_, elaborou dois ADRs (um sobre o JSON Schema e outro sobre fixar a versão do n8n), adicionou o template de issues no repositório, criou o arquivo `config.py` centralizando os caminhos dos diretórios para estruturação do código, renomeou o script `validator.py` para `schema_validator.py` e atualizou os documentos de escopo e arquitetura com a inclusão do Hacker News.

- **Para amanhã/Próximos passos:** Ajustar a PR para incorporar a alteração do nome da função de validação (`validate_data`), renomear a issue S1-06 para Stack Exchange, abrir e atribuir duas novas issues separadas para Hacker News e Mastodon para o Rodrigo, e conduzir a _Sprint Planning_ na segunda-feira às 19:30.

#### **Michael Dambock**

- **Feito hoje:** Alterou no script o nome da função de `validate_date` para `validate_data` (adequando a semântica à validação de dados), criou a branch `dataset_scenarios`, realizou a sincronização e a validação contra o JSON Schema, executando com sucesso o primeiro cenário real. Notou também que o exemplo de JSON ainda continha menção ao Open Router.

- **Para amanhã / Próximos passos:** Avaliar futuramente a inclusão da chave `synthetic` no Enum para acomodar fontes que exigem URLs reais nos testes de cenários sintéticos.

#### **Rodrigo Aguiar**

- **Feito hoje:** Confirmou a remoção da menção ao Open Router na PR S1-08 (já aprovada por Vitor) e estruturou os webhooks na tarefa S1-06, onde o fluxo WF04 faz requisições e salva o documento no bucket da OCI e o WF05 realiza o download. Identificou a ocorrência de valores nulos no campo `content_license` em algumas requisições e avançou na sanitização do corpo HTML das mensagens sem a utilização de nós de código customizados.

- **Para amanhã / Próximos passos:** Assumir as novas issues com a duplicação e manutenção dos fluxos independentes para Hacker News e Mastodon, e concluir a sanitização do corpo do texto em HTML.

#### **Ricieri Rosa**

- **Feito hoje:** Concluiu as alterações necessárias na documentação e estruturou o _boilerplate_ do projeto. Alinhou com Vitor a dúvida sobre a necessidade de rodar a aplicação em container.

- **Para amanhã / Próximos passos:** Finalizar a configuração do Docker para rodar o Streamlit em conjunto com a estrutura existente da aplicação.

#### **Gustavo Silva**

- **Feito hoje:** Não esteve presente nas falas síncronas da gravação, mas teve seu status avaliado durante o encerramento do ciclo semanal.

- **Para amanhã / Próximos passos:** Alinhar o andamento e a entrega da parte de desenvolvimento dos prompts.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                                 | Responsável   | Prazo / Status      |
| :----------------------------------------------------------------------------------- | :------------ | :------------------ |
| Renomear a issue S1-06 para Stack Exchange                                           | Vitor         | Imediato / A fazer  |
| Criar issues separadas para Hacker News e Mastodon e atribuir ao Rodrigo             | Vitor         | Imediato / A fazer  |
| Atualizar a PR com a alteração do nome da função para `validate_data`                | Vitor         | Próximo passo       |
| Implementar fluxos duplicados/específicos para Hacker News e Mastodon                | Rodrigo       | A iniciar           |
| Finalizar a sanitização de tags HTML no corpo das mensagens                          | Rodrigo       | Em andamento        |
| Analisar a viabilidade de adicionar a chave `synthetic` no Enum para URLs sintéticas | Michel        | Futuro / Em análise |
| Finalizar a configuração da aplicação Streamlit dentro do Docker                     | Riciere       | Em andamento        |
| Alinhar pendências relativas à criação de prompts                                    | Gustavo       | A verificar         |
| Atividades assíncronas no fim de semana e Sprint Planning na segunda às 19:30        | Toda a equipe | Definido / Agendado |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Sprint Planning (Início da Semana 2)

- **Data:** 26 de Outubro de 2026 (Segunda-feira)

- **Horário:** 19h30
