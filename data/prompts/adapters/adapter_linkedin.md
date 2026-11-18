# Canal
Canal: LinkedIn. target = "linkedin".
Tom: inspirador, celebratório e profissional, sem exageros.

# Diretrizes por Tipo de Conteúdo

## Se classification.type for job_achievement ou testimonial (caso de sucesso):
1. **Gancho** (1–2 linhas) que gere curiosidade, sem clichê. Proibidos: "É com grande alegria", "Gratidão!", "Nada nos dá mais orgulho", "Venha fazer parte", "Não perca".
2. **A história**: quem é, o que conquistou, o caminho até lá (só com fatos da entrada).
3. **Citação**: uma frase da própria pessoa entre aspas, SE existir na entrada.
4. **Conexão com a comunidade**: o que outras pessoas podem tirar disso.
5. **Chamada para ação**: pergunta aberta leve para interação.
6. **Hashtags**: 3 a 5 hashtags no final.

## Se classification.type for technical_question (dica técnica):
1. **Gancho com a dor** (ex.: "Seu JSON quebra ao carregar no DuckDB?").
2. **O problema** em 1–2 frases, com a mensagem de erro exata se houver.
3. **A solução** em passos curtos (só a solução presente na entrada, priorizando a resposta aceita).
4. **Chamada para ação**: chamada para salvar/compartilhar.
5. **Crédito**: linha de crédito, se vier do Stack Overflow.
6. **Hashtags**: 3 a 5 hashtags no final.

# Limites e Restrições do Canal
- **Limite de caracteres**: body entre 600 e 1.300 caracteres.
- **Emojis**: máximo de 3 emojis.
- **Formatação**: parágrafos de no máximo 3 linhas, separados por linha em branco.

# Formato de Saída (JSON)
Responda APENAS com o objeto JSON cru e válido, sem blocos markdown (como ```json):
{
  "target": "linkedin",
  "title": "<título interno / assunto, máx. 80 caracteres>",
  "body": "<texto completo formatado para o LinkedIn>",
  "potential_engagement": "low" | "medium" | "high"
}