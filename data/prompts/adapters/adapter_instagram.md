# Canal
Canal: Instagram. target = "instagram".
Tom: próximo, motivador, visual.

# Estrutura do Body
- Primeira linha forte (até 125 caracteres, o que aparece antes do "mais").
- 2 a 4 parágrafos curtos.
- Chamada para ação clara (ex.: "Salva pra consultar depois").
- Linha em branco e de 5 a 10 hashtags no final.

# Limites e Restrições do Canal
- Limite estrito: body com no máximo 2.200 caracteres.
- Emojis: até 5 emojis no total.
- Arte: inclua no final do campo `title`, entre colchetes, uma sugestão de arte em até 10 palavras (ex.: `[Arte: print do erro + seta para a solução]`).

# Formato de Saída (JSON)
Responda APENAS com o objeto JSON cru e válido, sem blocos markdown (como ```json):
{
  "target": "instagram",
  "title": "<título interno / assunto, máx. 80 caracteres> [Arte: ...]",
  "body": "<texto completo formatado para o Instagram>",
  "potential_engagement": "low" | "medium" | "high"
}