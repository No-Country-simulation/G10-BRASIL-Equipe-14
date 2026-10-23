# 📝 Ata de Reunião — Daily (Semana 1)

## Detalhes da Reunião

- **Projeto:** CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais | Hackathon - ONE G10
- **Data:** 21 de Outubro de 2026 (Quarta-feira, 20:00h)
- **Participantes Presentes:** Gustavo Silva, Michael Dambock, Ricieri Rosa, Rodrigo Aguiar, Rodrigo Silva, Vitor Pires
- **Ausências:** David Lima, Everton (sem contato desde o início do projeto)

---

## 1. Objetivo da Reunião

Alinhar as atividades realizadas ao longo do dia, atividades previstas e impedimentos/dificuldades encontradas.

---

## 2. Principais Pontos Discutidos e Status por Integrante

#### **Vitor Pires**

- **Feito hoje:** Verificou a API do Mastodon e analisou campos faltantes no mapeamento de campos canônicos das fontes de dados; compartilhou o JSON gerado no grupo. Testou a API do Bluesky (muito complexa) e analisou Hugging Face / GitHub (ausência de dados diretos de comentários).

- **Para amanhã/Próximos passos:** Aguardar correções na PR do Rodrigo (#53) e consolidar transcrições das reuniões na pasta do GitHub para manter o histórico do projeto.

- **Escopo de Redes/Canais:** Sugeriu focar inicialmente em **LinkedIn, X (Twitter) e Mastodon**.

#### **Gustavo Silva**

- **Atribuições:** Alocado nas _issues_ S103, S104, S105 e, em seguida, 8, 9 e 10.
- **Feito hoje:** Estruturou os 3 prompts iniciais do _router_ e o script de medição da taxa de acerto (_accuracy_). Testou preliminarmente em ambiente de testes.
- **Para amanhã/Próximos passos:** Testar os prompts com dados reais assim que o schema/JSON do Rodrigo/Michel for disponibilizado; testar nos 3 cenários obrigatórios (_conquista da vaga_, _dúvida técnica_, _ruído_) e abrir PR do _router_.
- **Observações/Dúvidas:** Questionou sobre padronização em inglês das chaves de saída (_output schema_) e observou ruídos/bots nos dados coletados (ex.: conteúdo em japonês marcado como inglês no Hacker News).

#### **Michael Dambock**

- **Feito hoje:** Trabalhou no _debugging_ e normalização dos JSONs coletados (Stack Exchange e Hacker News), validando 100/100 envelopes válidos. Desenvolveu script Python para normalização conjunta.
- **Discussão Técnica:** Defendeu manter o nome dos campos em **inglês** para evitar quebras/erros em integrações e ressaltou a importância de preservar metadados de auditoria (`content_license`, `owner`, `author`) por questões jurídicas/LGPD.
- **Outras ações:** Gravou a reunião e assumiu a responsabilidade de gerar e disponibilizar a transcrição e o resumo da Daily.

#### **Rodrigo Aguiar**

- **Feito hoje:** Trabalhou na issue **S01-08** (fluxo de requisições com paginação completa — 154 perguntas).
- **Desafios:** Encontrou limitação de _rate limit_ / tempo de requisição ao tentar coletar e mesclar campos como `content_license` e `comment_count`.
- **Para amanhã/Próximos passos:** Corrigir e otimizar o fluxo no n8n, exportar o JSON completo do fluxo e alinhar o envio dos dados de entrada para o Gustavo e o restante do time.

#### **Rodrigo Silva**

- **Feito hoje:** Desenvolveu pipelines de limpeza e normalização de dados para Hacker News, Stack Exchange e Mastodon, já criando a estrutura no banco de dados `.db`.
- **Para amanhã/Próximos passos:** Adequar os nomes das colunas para inglês e iniciar a estruturação da lógica de análise que será executada pela LLM.
- **Alinhamento:** Identificou sobreposição pontual com as tarefas do Michael, mas o time concordou que validações duplas no início ajudam na qualidade dos dados.

#### **Ricieri Rosa**

- **Feito hoje:** Desenvolveu o input_schema, o output_schema e um script de validação e teste.
- **Para amanhã/Próximos passos:** Após a revisão da PR enviada (#6), pretende focar na próxima issue (#12).

---

## 3. Deliberações e Ações Futuras (Action Items)

| Ação                                                                  | Responsável             | Prazo / Status              |
| :-------------------------------------------------------------------- | :---------------------- | :-------------------------- |
| Enviar JSON/Schema ajustado com dados reais                           | Rodrigo                 | Prioritário (Hoje / Amanhã) |
| Adequar normalização e nomes de campos para inglês                    | Michael / Rodrigo Silva | Em andamento                |
| Executar testes dos prompts com dados reais nos 3 cenários e abrir PR | Gustavo                 | Assim que receber os dados  |
| Notificar suporte sobre a ausência do integrante Éverton              | Vitor / Equipe          | A definir                   |
| Subir transcrição e ata (.md) para o repositório no GitHub            | Vitor / Michael         | Diário                      |

---

## 4. Próxima Reunião

- **Reunião Obrigatória:** Daily

- **Data:** 22 de Outubro de 2026 (Quinta-feira)

- **Horário:** 19h30
