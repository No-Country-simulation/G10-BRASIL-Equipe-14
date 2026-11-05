# 📝 Ata de Reunião — Daily (Semana 3)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 03 de Novembro de 2026 (Terça, 19h30)
- **Participantes Presentes:** Michael Dambock, Ricieri Rosa, Rodrigo Aguiar
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto), Gustavo Silva, Vitor Pires

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Resumo Executivo

A equipe realizou a sua reunião diária (_daily_) em **03/11/2026** para alinhar o andamento dos módulos das Semanas 2 e 3, registrando-se a ausência justificada de Vítor devido a avaliações acadêmicas. Entre as principais deliberações técnicas, **Michael** apresentou o módulo em Python de conexão com o Oracle Cloud Infrastructure (OCI) Object Storage (`/src/storage/oci_storage.py` - tarefa S2-04), discutindo com o time os critérios de aceitação do pacote de distribuição JSON, a padronização do cálculo semanal via calendário ISO (`ISO week`) e os critérios de idempotência na gravação dos dados. A equipe tratou também do desmembramento do _system prompt_ da tarefa S1-03 em arquivos menores (com separação de _skills_ e _output parser_) conduzido por **Rodrigo**, além da confirmação de encerramento das tarefas da Semana 1 (S1-02 e S1-09/Boilerplate). Por fim, **Ricieri** propôs uma mudança na condução das próximas _dailies_, passando a analisar o quadro Kanban da direita para a esquerda para focar no encerramento dos itens mais antigos antes de puxar novas demandas.

---

## 3. Principais Pontos Discutidos e Status por Integrante

#### **Michael Dambock**

- **Feito hoje:** Desenvolveu a primeira versão do script/módulo de conexão em Python com a OCI Object Storage (`/src/storage/oci_storage.py` - tarefa S204). Alinhou com a equipe os critérios de idempotência (evitando sobrescrever arquivos idênticos) e a definição do cálculo semanal utilizando o padrão ISO.

- **Para amanhã/Próximos passos:** Esclarecer com Vitor a origem exata do arquivo de configuração JSON do pacote de distribuição (se é gerado pelo Python ou n8n) e concluir as regras de gravação e sobrescrita na OCI.


#### **Ricieri Rosa**

- **Feito hoje:** Verificou o status da tarefa S1-01 (Boilerplate/Streamlit) e da tarefa S1-02 (ambas ajustadas, aguardando aprovação/fechamento final por Vítor). Propôs uma nova dinâmica para as reuniões diárias baseada na navegação do Kanban da direita para a esquerda.

- **Para amanhã / Próximos passos:** Estudar com mais profundidade a parte de Data Science/LLM do projeto para apoiar nas tarefas de integração e conduzir a próxima _daily_ focada na entrega das tarefas mais antigas.

#### **Rodrigo Aguiar**

- **Feito hoje:** Desmembrou o _system prompt_ único da tarefa S1-03 em arquivos menores e modulares no n8n (separando o prompt base, _skills_ de apoio e o _output parser_), criando conectores para reaproveitar essa estrutura nas tarefas S1-04 e S1-05. Esclareceu as peculiaridades da nomenclatura dos arquivos no _bucket_ da OCI (distinção entre a pasta `raw/` no bucket e a conversão `raw_` no download local).

- **Para amanhã / Próximos passos:** Finalizar a reestruturação dos prompts das tarefas S1-03, S1-04 e S1-05 e integrar o nó de _output parser_ padronizado para consumo de todas as IAs.

---

## 4. Deliberações e Ações Futuras (Action Items)

| Ação                                                                                   | Responsável     | Prazo / Status            |
| :------------------------------------------------------------------------------------- | :-------------- | :------------------------ |
| Confirmar a origem do pacote de distribuição JSON na tarefa S204 com Vítor             | Michael e Vitor | Em andamento              |
| Finalizar a implementação do script `oci_storage.py` com regras de idempotência        | Michael         | Em andamento              |
| Homologar o encerramento das tarefas S1-01 (Boilerplate) e S1-02 no Kanban             | Vitor           | Próximos passos           |
| Concluir o desmembramento do _system prompt_ e _output parser_ (S1-03, S1-04, S1-05)   | Rodrigo         | Em andamento              |
| Adotar a navegação da direita para a esquerda no Kanban durante as reuniões diárias    | Toda a equipe   | A partir da próxima daily |
---

## 5. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 04 de Novembro de 2026 (Quarta-feira)

- **Horário:** 19h30
