# 📝 Ata de Reunião — Daily (Semana 5)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 19 de Novembro de 2026 (Quinta-feira, 19h30)
- **Participantes Presentes:** Rodrigo Aguiar, Ricieri Rosa, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva, Michael Dambock

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou a sua reunião diária (*daily*) em **19/11/2026** para alinhar as principais pendências e atividades realizadas durante o dia. No fluxo de desenvolvimento, a PR **S3-04** foi aprovada e integrada à branch `develop`, enquanto a PR **S3-06** passou por revisão e aprovação por **Vitor**. **Rodrigo** avançou na PR **S4-01** com a homologação de 2 de 3 cenários concluídos, além de ter realizado testes de apresentação e vídeo no NotebookLM. No plano de infraestrutura e ambiente, **Vitor** identificou uma falha de execução no workflow **WF13** provocada pela atualização de versão do n8n (da v2.41.3 para a v2.47.7), demandando a atualização do Docker Compose e da documentação. Por fim, **Ricieri** atualmente se encontra na tarefa **S4-02** e desenvolveu um script automatizado para monitorar a disponibilidade de uma instância de máquina virtual (VM) no plano *Oracle Cloud Infrastructure (OCI) Always Free* para a realização do deploy da aplicação.

---

## 3. Principais Pontos Discutidos e Status por Integrante

### **Rodrigo Aguiar**

- **Feito hoje:** Concluiu os ajustes propostos na revisão da PR **S3-06**, avançou na homologação de 2 de 3 cenários da PR **S4-01**, e produziu uma apresentação e vídeo de teste no NotebookLM.

- **Para amanhã / Próximos passos:** Resolver os conflitos para realizar o *merge* da PR **S3-06** e dar continuidade à homologação da PR **S4-01**.

### **Vitor Pires**

- **Feito hoje:** Aprovou a PR **S3-04**, revisou e aprovou a PR **S3-06**. Identificou uma falha de execução no *workflow* **WF13**, constatando que ocorreu devido à atualização da versão do n8n (da v2.41.3 para a v2.47.7).

- **Para amanhã / Próximos passos:** Atualizar o Docker Compose e a documentação com a nova versão do n8n, além de atualizar a arquitetura do *pipeline* e o arquivo `README.md`.

### **Ricieri Rosa**

- **Feito hoje:** Criou um *script* automatizado para a tarefa **S4-02**, visando identificar e provisionar a melhor máquina virtual (VM) disponível no plano *Oracle Cloud Infrastructure (OCI) Always Free* para o *deploy* da aplicação.

- **Para amanhã / Próximos passos:** Dar continuidade ao desenvolvimento e execução da tarefa **S4-02**.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação | Responsável | Prazo / Status |
| :--- | :--- | :--- |
| Resolver conflitos e realizar o merge da PR S3-06 | Rodrigo Aguiar | Prioritário / Em andamento |
| Concluir a homologação dos cenários da PR S4-01 | Rodrigo Aguiar | Em andamento |
| Atualizar o Docker Compose e a documentação com a versão v2.47.7 do n8n | Vitor Pires | Em andamento |
| Atualizar o diagrama de arquitetura do pipeline e o arquivo README.md | Vitor Pires | Próximos passos |
| Executar script da task S4-02 para provisionamento de VM na OCI Always Free | Ricieri Rosa | Em andamento |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 20 de Novembro de 2026 (Sexta-feira)

- **Horário:** 19h30
