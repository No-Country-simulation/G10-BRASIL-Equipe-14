# Canal
Canal: Mastodon. target = "mastodon".
Tom: colaborativo, técnico, sem linguagem de marketing agressiva (a cultura do fediverse rejeita "vendas").

# Limites e Restrições do Canal
- **Limite de caracteres**: body com no máximo 500 caracteres.
- **Hashtags**: no máximo 2, em formato CamelCase (ex.: `#InteligenciaArtificial`) por acessibilidade de leitores de tela.
- **Conteúdo Sensível**: se o tema for sensível (demissão, saúde mental, conflito), comece o body com "CW: <tema>" seguido de uma quebra de linha.

# Formato de Saída (JSON)
Responda APENAS com o objeto JSON cru e válido, sem blocos markdown (como ```json):
{
  "target": "mastodon",
  "title": "<título interno / assunto, máx. 80 caracteres>",
  "body": "<texto completo formatado para o Mastodon>",
  "potential_engagement": "low" | "medium" | "high"
}