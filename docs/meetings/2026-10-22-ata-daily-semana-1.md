# 📝 Ata de Reunião — Daily (Semana 1)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 22 de Outubro de 2026 (Quinta-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva, Rodrigo Silva

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou um alinhamento sobre o andamento das tarefas do projeto, cobrindo integrações de fluxos, resolução de comentários em PRs, validação de cenários e atualização de documentação.

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Rodrigo Aguiar**

- **Feito hoje:** Desenvolveu a atividade S1-06, criando webhooks de gatilho para receber requisições e recuperar arquivos no bucket da OCI. Implementou o acionamento dos fluxos WF02 (coleta de perguntas via _comment count_) e WF03 (coleta de licenças via _content license_), além do merge de espera, download, unificação dos arquivos JSON com validação de dados e upload final para a OCI. Concluiu também o fluxo 05, que requisita o fluxo 04, baixa o JSON completo retornando código 200 via PowerShell e salva o arquivo em downloads. Demonstrou ainda a configuração de parâmetros dinâmicos de busca por _tag_, limite de páginas (100) e data.
- **Para amanhã/Próximos passos:** Liberar formalmente a atividade S1-06 com todos os fluxos e webhooks entre a noite de hoje e a manhã seguinte.

#### **Ricieri Rosa**

- **Feito hoje:** Solucionou todos os comentários, sugestões e correções do Pull Request (PR) aberto no dia anterior. O PR foi revisado pelo Vitor e teve o merge concluído na _branch_ principal. Criou a estrutura de um _volume_ para novos testes.
- **Para amanhã / Próximos passos:** Testar a viabilidade e o funcionamento do _volume_ e experimentar novos _scripts_, mantendo o foco nessa atividade já que não possui outras tarefas alocadas de imediato.

#### **Michael Dambock**

- **Feito hoje:** Elaborou os _drafts_ dos três cenários de teste e validação (Vagas, Dúvidas Técnicas e Ruído) para a tarefa 7, aguardando a aprovação e o merge do Participante 2 para poder prosseguir.
- **Para amanhã / Próximos passos:** Validar os três cenários com o esquema final após o merge concluído e definir o tratamento adequado para o campo `content license` em cada um deles.

#### **Vitor Pires**

- **Feito hoje:** Corrigiu a PR do N8N/OCI e atualizou a versão/imagem do N8N para eliminar erros que vinham ocorrendo nos _workflows_. Deu andamento à atualização dos documentos de escopo e arquitetura do projeto para incorporar formalmente o Hacker News como nova fonte de dados.
- **Para amanhã / Próximos passos:** Finalizar a revisão da documentação de escopo e arquitetura refletindo as novas integrações.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                         | Responsável    | Prazo / Status              |
| :--------------------------------------------------------------------------- | :------------- | :-------------------------- |
| Liberar a entrega da atividade S1-06 com os webhooks e fluxos integrados     | Rodrigo Aguiar | Hoje à noite ou amanhã cedo |
| Executar testes práticos de funcionamento no _Volume_                        | Ricieri        | Em andamento                |
| Validar os 3 cenários (_drafts_) com o esquema pós-merge                     | Michael        | Em andamento                |
| Ajustar a regra para o campo `content license` nos cenários de validação     | Michael        | Próximos passos             |
| Concluir a inclusão do Hacker News na documentação de escopo e arquitetura   | Vitor          | Em andamento                |
| Monitorar a estabilidade dos fluxos após atualização da imagem do N8N na OCI | Vitor          | Concluído                   |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 23 de Outubro de 2026 (Sexta-feira)

- **Horário:** 19h00
