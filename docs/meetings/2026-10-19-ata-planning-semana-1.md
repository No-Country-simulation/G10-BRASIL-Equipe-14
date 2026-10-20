# 📝 Ata de Reunião — Sprint Planning (Semana 1)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 19 de Outubro de 2026 (Segunda-feira)
- **Participantes Presentes:** Michael Dambock, Rodrigo Aguiar, Rodrigo Silva, Ricieri Rosa, Vitor Pires
- **Assunto:** Alinhamento técnico, divisão de tarefas da Semana 1 e infraestrutura de ingestão

---

## 1. Objetivo da Reunião

Alinhamento das atividades iniciais do projeto na **Semana 1**, focando no levantamento de dados de entrada, criação de prompts, ingestão/tratamento de dados e configuração de infraestrutura.

---

## 2. Principais Pontos Discutidos

1. **Organização e Divisão de Tarefas:**
    - As tarefas foram organizadas por área no GitHub Projects (Kanban).
    - Rodrigo Silva e Rodrigo Aguiar ficarão responsáveis pela ingestão dos dados de fontes como Stack Exchange e Mastodon.
    - Os dados coletados serão limpos, padronizados e organizados para posterior avaliação.

2. **Infraestrutura e Limitações:**
    - O ambiente n8n já está configurado na Oracle Cloud Infrastructure (OCI).
    - O servidor OCI em uso conta com 12 GB de RAM no plano gratuito (*Always Free*), proporcionando boa capacidade para o processamento com IA.
    - A equipe discutiu o formato dos dados trafegados e definiu o uso de **JSON** para entrada e saída, alinhado com o escopo do projeto.

3. **Restrições de Cotas e APIs:**
    - Foi levantada a preocupação com os limites de requisição de APIs gratuitas e lentidão em roteadores abertos (OpenRouter).
    - Como alternativa, sugeriu-se o uso compartilhado de chaves/APIs da equipe (fallback) ou o uso do Gemini Plus/Claude diretamente via chat para agilizar os testes de desenvolvimento.

4. **Rotina de *Dailies*:**
    - Ficou acordado realizar reuniões diárias (*dailies*) rápidas (10 a 15 minutos) para acompanhamento.
    - **Horário:** 19h30 (ou 20h00 nos dias sem compromissos prévios de membros da equipe).

---

## 3. Próximos Passos

- Atribuir os *cards* no GitHub Projects para cada responsável.
- Avançar na integração da fonte de dados Mastodon e Stack Exchange no n8n.
- Definir o *schema* e os campos do JSON de entrada/saída.
- Realizar a primeira *daily* no horário combinado (20 de Outubro, às 19h30).

---

## 4. Próxima Reunião

- **Reunião Obrigatória:** Daily.

- **Data:** 20 de Outubro de 2026 (Terça-feira).

- **Horário:** 19h30.
