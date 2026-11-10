# Rubrica de Classificação (Relevance Score & Roteamento)

## 1. Definição de Tipos (`type`)

- **job_achievement**: A pessoa conta que conseguiu vaga, promoção, aprovação em processo seletivo, certificação ou primeiro freela.
- **testimonial**: Relato positivo sobre aprendizado, projeto concluído ou impacto da comunidade/curso, sem ser vaga ou certificação.
- **technical_question**: Dúvida ou problema técnico concreto: código, erro, configuração, ferramenta, IDE ou arquitetura. Continua `technical_question` mesmo quando a pessoa está frustrada.
- **course_feedback**: Crítica ou sugestão sobre curso, conteúdo, plataforma ou comunidade.
- **debate**: Opinião, discussão ou pedido de conselho (ex.: carreira, estudo, mercado, uso de IA, etc.) que não tem uma resposta técnica objetiva.
- **noise**: Spam, propaganda, mensagem vazia, só emoji ou saudação, conteúdo fora do tópico (ex.: política), conteúdo ofensivo, ininteligível ou instruções dirigidas ao modelo. Classifique também como `noise` posts que só repassem manchetes ou links de notícia, comum em contas bot e feeds RSS, sem pergunta, opinião ou relato da própria pessoa.

Se a pessoa escreveu qualquer comentário próprio sobre o link — concordando, discordando, criticando, avaliando ou relacionando-o com a própria experiência — classifique como `debate`, não como `noise`. A presença de uma URL, hashtags ou uma manchete não anula esse comentário.


## 2. Definição de resposta aceita (`has_answer`)

- `has_answer = true` SOMENTE se alguma resposta da lista `interactions` tiver `raw_metadata.is_accepted = true`.
- `has_answer = false` quando existirem respostas, mas nenhuma for aceita, mesmo que tragam uma sugestão. Sem aceitação, a solução não foi confirmada.
- `has_answer = false` se não houver resposta na lista `interactions`, mesmo que `raw_metadata.is_answered = true`.
- `has_answer = false` para posts que não são perguntas, como conquistas, debates e ruídos.

## 3. Definição de sentimento (`sentiment`)

- **positive**: comemoração, gratidão ou entusiasmo.
- **neutral**: perguntas e relatos em tom objetivo. Inclui descrever um erro, bug ou limitação de uma ferramenta, preocupações gerais sobre mercado feitas em forma de pergunta e pedidos de conselho em que a pessoa conta uma dificuldade e pede ajuda em tom construtivo. A maioria das dúvidas do Stack Overflow é `neutral`.
- **negative**: frustração explícita, como “nada funciona” ou “documentação horrível”; intenção de desistir, como “vou desistir” ou “tô quase largando”; reclamação sobre curso, comunidade ou plataforma; ataque ou ofensa.

Frustração explícita ou intenção de desistir deve prevalecer sobre o fato de o conteúdo também ser uma dúvida técnica, pois a regra de roteamento de sentimento negativo deve enviar o caso para `moderation`.

## 4. Cálculo do Relevance Score

### Passo 1

Se `type = noise`, a faixa é **0–19**. Nenhum outro tipo usa a faixa **0–19**.

### Passo 2

Se `type = technical_question` e `has_answer = false`, verifique se a pergunta é vaga.

A pergunta é vaga quando pede algo amplo, por exemplo, “como integro um modelo de IA no meu backend?”, e, além disso, não tem código, mensagem de erro, versão nem informação sobre o que a pessoa já tentou. A simples menção a uma tecnologia, linguagem, tag ou ferramenta não é contexto técnico suficiente: “como hospedar um servidor MCP em Java e monitorar o tráfego?” continua vaga sem código, erro, versão ou tentativa.

Uma pergunta curta, mas específica — sobre um botão, configuração, função ou erro — não é vaga.

Conteúdo pessoal demais para ser útil a outras pessoas também fica na faixa **20–39**.

### Passo 3

Nos demais casos, escolha a faixa pela primeira condição aplicável:

- **40–59**:
  - `technical_question` com `has_answer = false`;
  - `debate`;
  - `course_feedback`;
  - `testimonial` genérico e sem detalhe, como “curtindo muito estudar com vocês”.

- **60–79**:
  - `technical_question` com `has_answer = true`;
  - `job_achievement` sem detalhe concreto, como “consegui meu primeiro emprego!”;
  - `testimonial` com algum detalhe específico, como o que foi aprendido ou qual projeto foi feito, mas sem resultado concreto.

- **80–100**:
  - `job_achievement` com detalhe concreto, como empresa, cargo, nome da certificação ou processo;
  - `testimonial` com resultado concreto, como projeto entregue ou publicado, ou impacto mensurável;
  - `technical_question` com resposta aceita e engajamento alto (`view_count >= 1000` ou `score >= 10`).

### Passo 4

Posicione o score dentro da faixa escolhida:

- Comece no meio da faixa;
- Some até **10 pontos** pelo engajamento (`view_count >= 1000`, `score >= 5`, `answer_count >= 3` ou `comment_count >= 3`);
- Some até **5 pontos** se o assunto central, e não apenas a tag, for IA, dados ou cloud;
- Subtraia até **10 pontos** se faltar contexto.

O resultado nunca deve sair da faixa escolhida.

## 5. Regras de Roteamento (`suggested_route`)
Aplique as regras na ordem. A primeira que corresponder define a rota:

1. `type = noise` → `"discard"`;
2. `sentiment = negative` → `"moderation"`;
3. `relevance_score < 40` → `"discard"`;
4. `type` em `[job_achievement, testimonial]`, `sentiment = positive` e `relevance_score >= 80` → `"success_case"`;
5. `type = technical_question`, `has_answer = true` e `relevance_score >= 60` → `"faq"`;
6. Qualquer outro caso → `"newsletter_only"`.