# 📝 Ata de Reunião — Daily (Semana 5)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 20 de Novembro de 2026 (Sexta-feira, 19h30)
- **Participantes Presentes:** Michael Dambock, Rodrigo Aguiar, Ricieri Rosa, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva
---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou a sua reunião diária (*daily*) em **20/11/2026** para consolidar os últimos ajustes técnicos e estratégicos antes do encerramento da *sprint*. No pilar de infraestrutura e *deploy*, em razão da indisponibilidade de instâncias *Always Free* (VMs de 12 GB+) na Oracle Cloud Infrastructure (OCI) e do tamanho elevado da imagem do n8n (~1,94 GB), o grupo decidiu priorizar o *deploy* da interface gráfica no **Streamlit Cloud** (vinculado à branch `main` do GitHub). Para garantir a validação completa, **Ricieri** realizará um teste pontual pago na OCI para homologar o código na nuvem. Na frente de desenvolvimento, **Vitor** avançou na revisão das tarefas **S4-01** (homologação) e **S4-06** (dicionário de dados), aguardando a submissão dos últimos PRs de **Rodrigo** para declarar o *code freeze*. No deck de slides, ajustou-se a substituição do slide 4 por um diagrama visual de arquitetura (Entrada -> Motor -> Saída) gerado por **Rodrigo**, além da ampliação do logotipo e remoção do slide de *Roadmap Futuro*. Por fim, definiu-se a gravação de um vídeo demonstrativo em ambiente real (*happy path* com postagem no LinkedIn) para servir de plano B contra imprevistos ao vivo, e relatou-se instabilidade na plataforma *No Country* ao tentar salvar a Avaliação 360º.

---

## 3. Principais Pontos Discutidos e Status por Integrante

### **Vitor Pires**
* **Feito hoje:** Conduziu a revisão de código das tarefas **S4-01** e **S4-06** (padronização de código e documentação), resolveu o problema de cache da imagem Docker do n8n atualizando as configurações e iniciou a validação de integração com o Streamlit Cloud.
* **Para amanhã / Próximos passos:** Finalizar a revisão dos últimos PRs de Rodrigo, atualizar o diagrama visual da arquitetura no repositório e conduzir a equipe ao *code freeze*.

### **Rodrigo Aguiar**
* **Feito hoje:** Trabalhou no encerramento dos seus *pull requests* pendentes, integrou as rotas de homologação e gerou o diagrama de arquitetura simplificado (Entrada -> Motor -> Saída) via Gemini/NotebookLM para incorporação aos slides.
* **Para amanhã / Próximos passos:** Submeter os PRs finais para aprovação de Vitor e realizar os testes de integração das rotas de saída.

### **Michael Dambock**
* **Feito hoje:** Resolveu pendências técnicas de áudio com periféricos e ajustou o deck de slides (incorporou a nova imagem de arquitetura no slide 4, removeu o *Roadmap Futuro* e ajustou o tamanho da marca do *Community Lab*).
* **Para amanhã / Próximos passos:** Finalizar os retoques estéticos na apresentação e participar da gravação do vídeo demonstrativo em *happy path*.

### **Ricieri Rosa**
* **Feito hoje:** Analisou os gargalos de infraestrutura e limitações das instâncias *Always Free* na OCI (destacando o tamanho da imagem do n8n de ~1,94 GB) e sugeriu a realização de um teste pontual pago na OCI para certificar o funcionamento do código.
* **Para amanhã / Próximos passos:** Validar o teste na OCI, verificar os *endpoints* públicos de comunicação com o Streamlit e apoiar no roteiro do vídeo de demonstração.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação | Responsável | Prazo / Status |
| :--- | :--- | :--- |
| Priorizar o *deploy* da interface no Streamlit Cloud conectado à branch `main` | Vitor e Rodrigo | Prioritário / Em andamento |
| Realizar teste pontual na OCI para homologar a execução do código na nuvem | Ricieri Rosa | Em andamento |
| Concluir a revisão das tarefas S4-01 e S4-06 e realizar o *code freeze* | Vitor Pires | Em andamento |
| Atualizar o deck de slides (inserir diagrama de arquitetura e remover Roadmap Futuro) | Michael Dambock | Em andamento |
| Gravar vídeo demonstrativo completo (*happy path* com publicação real no LinkedIn) | Toda a equipe | Até 22/11 (Domingo) |
| Tentar novamente o preenchimento e salvamento da Avaliação 360º na plataforma | Toda a equipe | Até 22/11 (Domingo) |

---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Sprint Planning (Início da Semana 6)

- **Data:** 23 de Novembro de 2026 (Segunda-feira)

- **Horário:** 19h30

Aqui está a **Ata de Reunião do dia 20/11/2026** totalmente estruturada e padronizada conforme o modelo adotado para o projeto:
