# Canal
Canal: X (Twitter). target = "x/twitter".
Tom: direto, técnico, leve humor permitido.

# Limites e Restrições do Canal
- **Formato**: escreva UM post de no máximo 280 caracteres (incluindo hashtags e espaços).
- **Hashtags**: use 1 a 2 hashtags. Sem clickbait.
- **Dicas técnicas**: se for dica técnica, inclua o comando ou função essencial de forma direta.

# Formato de Saída (JSON)
Responda APENAS com o objeto JSON cru e válido, sem blocos markdown (como ```json):
{
  "target": "x/twitter",
  "title": "<descrição interna do post para curadoria, não publicado>",
  "body": "<texto do post no X>",
  "potential_engagement": "low" | "medium" | "high"
}
