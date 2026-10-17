# ADR-001: Definição do escopo e stack base

* **Status:** Aprovado
* **Data de Elaboração:** 17 de Outubro de 2026
* **Autores:** Equipe 14 - Turma G10

---

## Sumário

* [1. Contexto e Problema](#1-contexto-e-problema)
* [2. Decisão Tomada](#2-decisão-tomada)
* [3. Consequências](#3-consequências)
  * [3.1. Prós / Vantagens](#31-prós--vantagens)
  * [3.2. Contras / Limitações e Riscos Mitigados](#32-contras--limitações-e-riscos-mitigados)
    
---

## 1. Contexto e Problema

Desenvolvimento do projeto **CommunityLab**, uma solução de IA para monitoramento de comunidade e geração automatizada de ativos de conteúdo.

Dentre os quatro possíveis focos de solução propostos pelo briefing (gerador de conteúdo, detector de histórias, motor de FAQ/educativo e dashboard analítico) e os seguintes requisitos:

1. Escolher um nicho técnico para extração de dados viável sem custos de API.
2. Garantir 100% de conformidade com a gratuidade integral (camada Always Free da Oracle e LLMs gratuitas).
3. Entregar um fluxo funcional em 6 semanas com pipeline orquestrado, interface de curadoria humana (*Human-in-the-Loop*) e persistência em nuvem.

---

## 2. Decisão Tomada

A equipe decidiu os seguintes pontos:

1. **Foco do MVP:** 
Construir o **Motor de FAQ Dinâmico e Conteúdo Educativo**, transformando dúvidas técnicas recorrentes e discussões da comunidade em tutoriais curtos, tópicos de FAQ e publicações especializadas para redes sociais.

2. **Fontes de Dados Primárias:** 
Ingestão a partir do **Stack Exchange / Stack Overflow API** e instâncias públicas do **Mastodon**, focando inicialmente no tópico de *_Inteligência Artificial_*. 

    * Foi sugerida como alternativa o dataset [LMSYS](https://huggingface.co/datasets/lmsys/lmsys-chat-1m) do Hugging Face como um complemento às demais fontes.

3. **Orquestração de Workflows:** **n8n Self-Hosted via Docker (Local)** na fase de desenvolvimento, com exportação dos fluxos em JSON para o repositório.

4. **Tratamento e Engenharia de Dados:** Avaliação e uso de **DuckDB** para limpeza, normalização e agregação ultrarrápida dos dados brutos antes da triagem da IA.

5. **Provedor de LLM:** **Google Gemini API** (camada gratuita) ou alternativas gratuitas via Groq, Nvidia API ou Ollama em caso de limitações de quota.

6. **Persistência Obrigatória:** **OCI Object Storage (Camada Always Free)** para armazenamento dos pacotes de ativos consolidados em formato JSON (`pacote-distribuicao.json`).

7. **Deploy em Nuvem (Diferencial):** Subida do n8n e Streamlit em VM Linux na OCI (Compute Always Free) postergada como entrega diferencial/opcional das Semanas 4/5.

---

## 3. Consequências

### 3.1. Prós / Vantagens

* **Custo Zero Real:** Nenhuma dependência de cartões de crédito para APIs comerciais (OpenAI/Claude) ou ferramentas SaaS pagas (n8n Cloud oficial).

* **Viabilidade Técnica Imediata:** APIs abertas (Stack Exchange e Mastodon) não impõem os bloqueios severos de plataformas como X/Twitter ou LinkedIn.

* **Alinhamento com o Edital:** Cumpre os critérios de persistência no OCI Object Storage, nós condicionais no n8n e geração de múltiplos formatos (LinkedIn, Newsletter, FAQ).

* **Desempenho com DuckDB:** Redução drástica de overhead computacional para manipulação analítica local sem necessidade de manter um servidor de banco pesado rodando.

### 3.2. Contras / Limitações e Riscos Mitigados

* **Restrições de Hardware da OCI:** A camada *Always Free* tem limites de RAM e CPU. 
    * *Mitigação:* manter a fase de prototipagem em Docker local e só migrar o container n8n para a VM da Oracle após os fluxos estarem estabilizados.

* **Heterogeneidade de Dados:** Discussões técnicas costumam ter ruídos, códigos longos e múltiplos idiomas. 
    * *Mitigação:* implementação de nós de sanitização e prompts com instruções rígidas de normalização.
