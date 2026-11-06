# Rubrica de Classificação (Relevance Score & Roteamento)

## 1. Definição de Tipos (`type`)
- **job_achievement**: Conquista de vaga, promoção, aprovação em processo seletivo ou certificação.
- **testimonial**: Relato positivo sobre aprendizado, projeto concluído ou impacto.
- **technical_question**: Dúvida ou problema técnico concreto (código, erro, configuração, arquitetura).
- **course_feedback**: Crítica ou sugestão sobre curso ou plataforma.
- **debate**: Opinião, discussão ou pedido de conselho sem resposta técnica exata.
- **noise**: Spam, propaganda, mensagens vazias, saudações isoladas ou posts que apenas repassam manchetes de links de notícias sem autoria ou opinião (comum em RSS bots). *Exceção:* Se houver opinião crítica ou análise pessoal sobre o link, classifique como **debate**.

## 2. Cálculo do Relevance Score (4 Passos)
- **Passo 1:** Se `type = noise`, a faixa é **0–19**.
- **Passo 2:** Se `type = technical_question` e `has_answer = false`, verifique se a pergunta é vaga (ampla demais, sem código, erro ou contexto). Se for vaga, faixa **20–39**.
- **Passo 3:** Nos demais casos, defina a faixa base:
  - **80–100**: Conquistas detalhadas com empresa/cargo; depoimentos com impacto mensurável; dúvidas técnicas de alto impacto com resposta aceita e forte engajamento (`view_count >= 1000` ou `score >= 10`).
  - **60–79**: Dúvidas técnicas com resposta aceita; conquistas genéricas; depoimentos específicos sem métrica de impacto.
  - **40–59**: Dúvidas sem resposta; debates; feedbacks; depoimentos genéricos.
- **Passo 4:** Ajustes finos: adicione até +10 por engajamento alto e +5 se o núcleo for IA, dados ou cloud. Subtraia até -10 se faltar contexto crítico.

## 3. Regras de Roteamento (`suggested_route`)
A primeira regra que atender à condição define a rota:
1. `type = noise` $\rightarrow$ `"discard"`
2. `sentiment = negative` $\rightarrow$ `"moderation"` (nunca gerar conteúdo público de desabafos ou reclamações)
3. `relevance_score < 40` $\rightarrow$ `"discard"`
4. `type` em `[job_achievement, testimonial]` E `sentiment = positive` E `relevance_score >= 80` $\rightarrow$ `"success_case"`
5. `type = technical_question` E `has_answer = true` E `relevance_score >= 60` $\rightarrow$ `"faq"`
6. Demais casos $\rightarrow$ `"newsletter_only"`