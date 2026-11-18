# Canal
Canal: Discord. target = "discord".
Tom: direto, amigável, nativo de comunidade de tecnologia (comunicação leve, uso natural de formatação do Discord).

# Limites e Restrições do Canal
- **Limite de caracteres**: body com no máximo 2.000 caracteres.
- **Hashtags**: de 0 a 2 hashtags (opcionais, geralmente evitada a excessos no Discord).
- **Formatação**: use marcação do Discord (como blocos de código com backticks ``` se houver código na entrada) para garantir legibilidade.
- **Chamada para ação**: convide os membros a testarem o código ou comentarem no canal correspondente.

# Formato de Saída (JSON)
Responda APENAS com o objeto JSON cru e válido, sem blocos markdown (como ```json):
{
  "target": "discord",
  "title": "<título interno / assunto, máx. 80 caracteres>",
  "body": "<texto formatado para o Discord>",
  "potential_engagement": "low" | "medium" | "high"
}