Hackathon ONE G10 — Oracle Next Education & Alura

# Projeto 3 – 🚀 CommunityLab – Motor Inteligente de Transformação e Distribuição para Comunidades Digitais

## Mapeamento de Formações ONE (Grupo 10)

- Formações Indispensáveis: Desarrollo y Orquestación con IA Generativa, Engenharia de Agentes e Automação e Oracle Cloud Infrastructure (OCI).

- Formações de Reforço: Inteligência de Dados e RAG Avançado.

- Núcleo Técnico: Engenharia de prompts e copywriting persuasivo para múltiplos canais, automação de fluxos de curadoria com nós condicionais e persistência de ativos no OCI Object Storage na camada Always Free.

## Setor empresarial

MarTech / Gestão de Comunidades Digitais / Marketing de Conteúdo & Engajamento — Soluções inteligentes voltadas para comunidades de aprendizagem, ecossistemas de desenvolvedores, empresas SaaS e criadores de conteúdo. O setor precisa monitorar grandes volumes de conversas orgânicas, dúvidas, feedbacks, entregas de projetos e depoimentos dispersos em canais digitais (Discord, Slack, Fóruns, GitHub, Formulários) e transformá-los de maneira sistemática em ativos de marketing, crescimento e retenção.

## Descrição do projeto

Desenvolver uma solução inteligente e automatizada capaz de ingerir a atividade orgânica de uma comunidade digital (mensagens, debates em fóruns, feedbacks de cursos, entregas de projetos de alunos, interações em chats), analisar esses dados e convertê-los automaticamente em ativos de distribuição prontos para publicação e tomada de decisão. Hoje, comunidades vibrantes geram diariamente dezenas de histórias inspiradoras, dúvidas recorrentes e feedbacks valiosos, mas a maioria desse valor se perde no histórico dos canais porque a curadoria e a produção manual de conteúdo de marketing consomem muitas horas das equipes de Community Management e Marketing. O CommunityLab permite que a equipe escolha e construa uma solução focada dentro desse problema, como por exemplo:

- Gerador Automático de Conteúdo para Redes Sociais: Criação de posts estruturados para LinkedIn, X (Twitter) e Newsletters a partir de debates e vitórias da comunidade;

- Detector Inteligente de Histórias de Sucesso e Testemunhos: Identificação de relatos de superação, conquistas de vagas e projetos de destaque com extração de citações e cases prontos para marketing;

- Motor de FAQ Dinâmico e Conteúdo Educativo: Transformação de dúvidas frequentes dos alunos em tutoriais rápidos, dicas da semana e tópicos de documentação;

- Dashboard de Saúde e Sentimento da Comunidade: Análise contínua do sentimento dos membros, detecção de tópicos em alta e alertas de membros que precisam de apoio.

A inteligência da aplicação deverá:

1. Ingerir dados de interações em lote ou tempo real (via JSON, CSV, Webhook ou integração com plataformas);

2. Processar o conteúdo com LLMs de escolha da equipe (Google Gemini, OpenAI ChatGPT, Anthropic Claude ou equivalentes), analisando sentimento, tópicos e relevância comunicacional;

3. Orquestrar workflows automatizados (utilizando n8n, LangChain/LangGraph ou scripts Python equivalentes) para redigir copies otimizados para diferentes canais de distribuição;

4. Armazenar os ativos gerados e relatórios no OCI Object Storage (camada Always Free).

## Necessidade do cliente (explicação não técnica)

Os times de marketing e gestão de comunidade passam horas navegando por mensagens soltas no Discord ou Slack tentando encontrar depoimentos espontâneos de alunos ou pensando no que postar nas redes sociais da instituição. A solução deve permitir:

- Capturar automaticamente o que está acontecendo na comunidade sem esforço manual;

- Identificar quem teve uma grande conquista ou dúvida interessante de forma instantânea;

- Gerar posts persuasivos e prontos para publicar no LinkedIn e Twitter, respeitando a voz da marca;

- Criar resumos semanais de comunidade (*Community Highlights*) em segundos;

- Monitorar o sentimento geral, identificando se a comunidade está engajada, satisfeita ou com dificuldades.

## Validação de mercado

O conceito de Community-Led Growth (Crescimento Orientado por Comunidades) e Marketing de Conteúdo orientado por IA é uma das maiores tendências no ecossistema global de tecnologia:

- Conteúdos autênticos gerados por usuários (User Generated Content - UGC) possuem taxas de conversão e engajamento até 4x maiores do que propagandas corporativas tradicionais.

- A automação de fluxos com IA (n8n + LLMs) elimina o trabalho braçal de coleta e redação, permitindo que times enxutos publiquem conteúdos de alta qualidade diariamente.

- Plataformas que monitoram sentimento e geram ativos sistemáticos transformam a comunidade em um motor sustentável de aquisição de novos alunos e retenção de talentos.

## Objetivo do Hackathon

Desenvolver um MVP funcional de motor inteligente de conteúdo capaz de:

1. Processar dados de atividades e interações de uma comunidade digital (dados simulados ou reais);

2. Realizar análise de sentimento, categorização de tópicos e identificação de histórias/insights relevantes utilizando LLMs (Google Gemini, OpenAI, Claude ou outros modelos);

3. Orquestrar a geração automática de pelo menos dois formatos distintos de ativos de marketing/distribuição (ex.: Post para LinkedIn + Resumo Semanal da Comunidade, ou Case de Depoimento + Tópico de FAQ);

4. Implementar a automação do fluxo utilizando n8n (com nós de IA) ou pipelines em Python (LangChain / LangGraph) ou equivalentes;

5. Disponibilizar uma interface amigável (Streamlit / Gradio) ou painel de curadoria/aprovação;

6. Integrar a solução obrigatoriamente com o OCI Object Storage (camada Always Free).

## Resultados esperados

### 1. IA, Processamento de Texto & Geração de Copy

Notebook ou módulos contendo:

- Ingestão e limpeza de dados de conversas/feedbacks da comunidade;

- Análise de sentimento e extração de entidades/tópicos com LLMs;

- Cadeias de prompt engineering especializadas em copywriting para diferentes canais (LinkedIn, X, Newsletter);

- Mecanismo de pontuação de relevância para selecionar os melhores momentos da comunidade.

### 2. Automação de Fluxos & Interface

Workflow em n8n ou aplicação Python contendo:

- Fluxo automatizado integrando gatilhos (Webhook, Google Sheets, Formulário ou Chat) com nós de inteligência artificial;

- Ramificação de condições (ex.: se sentimento for extremamente positivo -> gerar Case de Sucesso; se for dúvida recorrente -> gerar Dica/FAQ);

- Interface web interativa (Streamlit ou Gradio) para visualização dos dados da comunidade e aprovação dos posts gerados.

### 3. Oracle Cloud Infrastructure (OCI) — Camada Always Free

- Requisito Obrigatório (MVP): OCI Object Storage — Criação de Bucket Always Free para armazenar os pacotes de ativos gerados (textos formatados, relatórios e JSONs);

- Recurso Opcional / Diferencial: OCI Compute Instance ("Deploy Completo em Nuvem") — Hospedagem da aplicação ou container n8n em máquina virtual Linux Always Free na OCI;

- Aviso Importante ONE: Utilize exclusivamente recursos da camada Always Free da OCI, mantendo a conformidade com a gratuidade integral do programa social ONE.

### 4. Documentação & Demonstração

- Repositório no GitHub com histórico de commits organizado;

- README.md completo com diagrama de arquitetura do pipeline e guia passo a passo de implantação;

- Demonstração prática apresentando o processamento de um lote de mensagens da comunidade e a geração simultânea dos ativos de distribuição.

## Funcionalidades obrigatórias (MVP)

### Endpoint / Ação: Processamento de Atividade e Geração de Ativos

O sistema deve receber um conjunto de mensagens/interações da comunidade e retornar a análise consolidada acompanhada dos ativos de marketing prontos para uso.

### Exemplo de Requisição (Entrada):

```json
{
  "origem_comunidade": "Discord_Grupo_ONE_G10",
  "periodo_referencia": "Semana_04",
  "interacoes": [
    {
      "autor": "Mariana Souza",
      "canal": "#conquistas-e-vagas",
      "tipo": "depoimento",
      "texto": "Pessoal, passei no processo seletivo para Desenvolvedora Júnior de IA! O projeto do curso de LangChain e OCI que construi no portfólio fez toda a diferenca na entrevista tecnica. Muito grata a comunidade pelo apoio!"
    },
    {
      "autor": "Lucas Albuquerque",
      "canal": "#duvidas-langgraph",
      "tipo": "pergunta_tecnica",
      "texto": "Estou com duvida de como estruturar os nós condicionais no LangGraph quando a resposta do Gemini precisa de retry. Alguem tem um exemplo pratico de router?"
    }
  ]
}
```

### Exemplo de Resposta (Saída Estruturada):

```json
{
  "status": "sucesso",
  "resumo_comunidade": {
    "total_interacoes_processadas": 2,
    "sentimento_predominante": "Altamente Positivo",
    "topicos_principais": [
      "Contratacao / Conquistas",
      "LangGraph / Nós Condicionais"
    ]
  },
  "ativos_distribuicao_gerados": {
    "post_linkedin": {
      "titulo": "Da Comunidade para o Mercado: O impacto dos projetos praticos de IA",
      "copy": "Nada nos dá mais orgulho do que ver nossos talentos conquistando o mercado de tecnologia! 🚀\n\nA aluna Mariana Souza acaba de ser contratada como Desenvolvedora Júnior de IA após destacar seus projetos práticos desenvolvidos com LangChain e Oracle Cloud Infrastructure.\n\nHistorias como a da Mariana comprovam: construir solucoes reais e o melhor caminho para acelerar a carreira tech. Parabens, Mariana! 👏\n\n#TalentosTech #InteligenciaArtificial #OracleCloud #CarreiraDev",
      "canal_recomendado": "LinkedIn Oficial",
      "potencial_engajamento": "Alto"
    },
    "destaque_newsletter_semanal": {
      "secao": "Vitoria da Semana",
      "chamada": "Aluna conquista vaga dev com portfólio de IA na Oracle Cloud",
      "resumo": "Mariana Souza conquistou sua primeira oportunidade como Dev Jr de IA destacando projetos desenvolvidos durante a formação."
    },
    "sugestao_conteudo_faq": {
      "tema": "Dica Rapida: Como criar nós de retry no LangGraph",
      "origem": "Duvida frequente levantada por Lucas Albuquerque no canal de suporte",
      "status": "encaminhado_para_mentoria"
    }
  },
  "armazenamento_oci": {
    "bucket": "communitylab-ativos-marketing",
    "caminho_objeto": "ativos/2026-semana-04/pacote-distribuicao.json",
    "status": "salvo_com_sucesso"
  }
}
```

## Requisitos mínimos (Checklist de Avaliação)

- [ ] Ingestão funcional de interações da comunidade (mensagens, CSV ou JSON simulando canais);

- [ ] Análise de sentimento e extração de tópicos utilizando LLMs (Google Gemini, OpenAI, Claude ou equivalentes);

- [ ] Geração automatizada de pelo menos 2 formatos de ativos de marketing (ex.: Post LinkedIn + Newsletter ou FAQ + Case de Sucesso);

- [ ] Orquestração do fluxo utilizando n8n ou Python (LangChain / LangGraph) ou ferramentas equivalentes;

- [ ] Integração ativa com o OCI Object Storage (camada Always Free) para armazenar os pacotes de ativos gerados;

- [ ] Demonstração de no mínimo 3 exemplos de transformação de interações em ativos de publicação;

- [ ] Repositório no GitHub com documentação e diagrama da esteira de distribuição.

## Recursos opcionais (Diferenciais)

- Deploy Completo em Nuvem (OCI Compute): Hospedagem da aplicação ou container n8n em máquina virtual Linux Always Free na OCI;

- Fluxo Completo de Automação no n8n: Webhook recebendo mensagens diretamente de formulários ou Discord e gerando rascunhos no Google Docs ou disparando e-mails;

- Bot Interativo de Comunidade: Assistente no Discord/Telegram que responde dúvidas técnicas e sinaliza depoimentos automaticamente;

- Painel de Curadoria em Streamlit: Interface visual para o time de marketing editar, aprovar e publicar os posts gerados com um clique;

- Geração de Imagens para Posts: Criação de cards comemorativos ou banners para redes sociais utilizando ferramentas multimodais.

## Diretrizes técnicas para os estudantes

### IA Generativa & Engenharia de Prompts

- Modelos de Linguagem: As equipes têm total autonomia para escolher entre Google Gemini, OpenAI (ChatGPT / GPT-4o), Anthropic (Claude), Grok ou modelos locais/open-source;

- Engenharia de Prompts: Ajuste os system prompts para garantir tons de voz adequados para cada canal (tom inspirador no LinkedIn, conciso no Twitter/X, didático no FAQ);

- Few-Shot Learning: Utilize exemplos no prompt para ensinar o modelo a replicar o estilo de comunicação desejado.

### Automação & Workflows

- Tecnologias Sugeridas: n8n para automação de fluxos com nós de IA e integrações com Slack/Gmail/Sheets, e Streamlit ou Gradio para interfaces de controle;

- Flexibilidade: Soluções em Python puro, Node.js ou outras plataformas de automação (ex.: Make) são plenamente aceitas.

### Oracle Cloud Infrastructure (OCI)

- Object Storage (Obrigatório): Persista todos os pacotes de ativos gerados em um Bucket Always Free;

- Atenção aos Custos: Mantenha o uso restrito aos recursos gratuitos da camada Always Free.
