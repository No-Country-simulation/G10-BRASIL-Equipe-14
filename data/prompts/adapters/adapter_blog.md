# Canal
Canal: Blog. target = "blog".
Tom: educacional, estruturado, analítico e aprofundado (estilo artigo técnico ou post de medium/dev.to).

# Estrutura do Body (Markdown)
1. **Introdução** (1-2 parágrafos): apresenta o problema ou conquista com ganchos claros.
2. **Desenvolvimento**: detalha o passo a passo técnico, a solução aplicada ou a história de sucesso com base estrita nos dados de entrada.
3. **Conclusão / Lições aprendidas**: o que a comunidade pode extrair desse aprendizado.

# Limites e Restrições do Canal
- **Limite de caracteres**: body entre 500 e 5.000 caracteres.
- **Hashtags**: de 0 a 5 hashtags no final do artigo.
- **Título**: o campo `title` deve ter no máximo 120 caracteres, sendo claro e atrativo para leitura em feed de artigos.

# Formato de Saída (JSON)
Responda APENAS com o objeto JSON cru e válido, sem blocos markdown (como ```json):
{
  "target": "blog",
  "title": "<título do artigo, máx. 120 caracteres>",
  "body": "<artigo completo formatado em Markdown>",
  "potential_engagement": "low" | "medium" | "high"
}