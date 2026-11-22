# 📝 Ata de Reunião — Daily (Semana 5)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 18 de Novembro de 2026 (Quarta-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Rodrigo Aguiar, Ricieri Rosa, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou a sua reunião diária (*daily*) em **18/11/2026** para alinhar os últimos ajustes técnicos e administrativos rumo à entrega final do Hackathon (marcada para domingo, 22/11, às 23h59). No pilar de desenvolvimento e testes, **Vitor** concluiu a revisão dos Pull Requests das tarefas **S3-04** e **S3-06**, corrigindo parâmetros em testes dos *adapters*, enquanto **Rodrigo** avançou na tarefa **S4-01** e implementou o rastreamento (*tracing*) dos agentes via **LangSmith** para monitoramento de latência, etapas de execução e consumo de tokens. Na infraestrutura, **Ricieri** enfrentou um bloqueio na Oracle Cloud Infrastructure (OCI) devido à falta de capacidade da região (*Out of Host Capacity*) ao tentar provisionar a VM da tarefa **S4-02**, assumindo também a criação do documento unificado de dicionário de dados (`docs/dicionario_dados.md` / **S4-06**). Nos preparativos do *pitch*, **Michael** apresentou a versão atualizada dos slides (10 páginas), incluindo a marca do *Community Lab*, ajustando a métrica real para "mais de 397 interações consolidadas" e demarcando a demonstração prática entre os slides 6 e 7. Por fim, o grupo definiu a estratégia para o preenchimento diário das avaliações 360º e autoavaliações, alinhando a inclinação de manter apenas um apresentador no *Demo Day* para evitar falhas de conexão.

---

## 3. Principais Pontos Discutidos e Status por Integrante

### **Rodrigo Aguiar**
* **Feito hoje:** Implementou o rastreamento (*tracing*) dos agentes com **LangSmith** (capturando metadados, etapas de execução e consumo de tokens), avançou na homologação dos cenários da tarefa **S4-01** e disponibilizou um ambiente no **NotebookLM** contendo os materiais do projeto para apoiar a equipe na preparação de perguntas e respostas da banca.
* **Para amanhã / Próximos passos:** Concluir a homologação da tarefa **S401**, atualizar a branch para o *merge* da PR **S3-04** e unificar as especificações no dicionário de dados (**S406**).

### **Vitor Pires**
* **Feito hoje:** Concluiu a revisão dos PRs **S304** e **S306**, corrigiu dois parâmetros faltantes nos testes dos *adapters* e deu início à atualização do diagrama de arquitetura do *pipeline*.
* **Para amanhã / Próximos passos:** Finalizar a atualização do diagrama de arquitetura, atualizar o arquivo `README.md`, conduzir a revisão geral do código (**S4-04**) e acompanhar a unificação da documentação.

### **Michael Dambock**
* **Feito hoje:** Refatorou o deck de slides da apresentação (10 páginas), corrigiu termos e vícios de linguagem, adicionou o logotipo do *Community Lab* em todas as telas, ajustou a métrica de resultado para "mais de 397 interações consolidadas" e demarcou o intervalo da demonstração ao vivo entre os slides 6 e 7.
* **Para amanhã / Próximos passos:** Concluir os últimos ajustes nos slides, remover inconsistências de texto apontadas pelo grupo e gravar o vídeo individual de apresentação.

### **Ricieri Rosa**
* **Feito hoje:** Tentou o provisionamento da instância VM no plano *Always Free* da OCI (tarefa **S4-02**), identificando indisponibilidade de capacidade na região (*Out of Host Capacity*), e assumiu a tarefa **S4-06** para consolidar a documentação do dicionário de dados.
* **Para amanhã / Próximos passos:** Tentar novamente o provisionamento da VM na OCI pela manhã (avaliando mudança de imagem se necessário) e estruturar o arquivo `docs/dicionario_dados.md` com as credenciais do n8n e APIs (**S4-06**).

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação | Responsável | Prazo / Status |
| :--- | :--- | :--- |
| Concluir a homologação dos *workflows* (S4-01) e realizar o *merge* da PR S3-04 | Rodrigo Aguiar | Prioritário / Em andamento |
| Tentar novo provisionamento de VM no plano *Always Free* da OCI (S4-02) | Ricieri Rosa | Em andamento / Tentativa matinal |
| Unificar o dicionário de dados e credenciais em `docs/dicionario_dados.md` (S4-06) | Ricieri e Rodrigo | Em andamento |
| Atualizar o diagrama de arquitetura do *pipeline* e o arquivo `README.md` | Vitor Pires | Em andamento |
| Realizar ajustes finos nos slides e fixar as métricas oficiais de engajamento | Michael Dambock | Em andamento |
| Preencher uma avaliação 360º / autoavaliação por dia na plataforma | Toda a equipe | Até 22/11 (23h59) |
| Realizar ensaio geral cronometrado (5 min) e testar a condução por 1 apresentador | Toda a equipe | Antes do Demo Day |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 19 de Novembro de 2026 (Quinta-feira)

- **Horário:** 19h30
