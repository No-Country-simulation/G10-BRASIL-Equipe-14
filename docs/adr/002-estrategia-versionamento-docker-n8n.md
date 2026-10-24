# ADR-002: Estratégia de Versionamento e Fixação de Imagens Docker (Patch Pinning)

- **Projeto:** CommunityLab - Motor Inteligente
de Transformação e Distribuição para Comunidades Digitais
- **Responsáveis:** Equipe 14 - Turma G10
- **Status:** Aprovado
- **Data de Elaboração:** 23 de Outubro de 2026

---

## Sumário

- [1. Contexto e Problema](#1-contexto-e-problema)
- [2. Decisão Tomada](#2-decisão-tomada)
- [3. Consequências](#3-consequências)
  - [3.1. Prós / Vantagens](#31-prós--vantagens)
  - [3.2. Contras / Limitações e Riscos Mitigados](#32-contras--limitações-e-riscos-mitigados)
    
---

## 1. Contexto e Problema

Durante o alinhamento de ambientes entre o desenvolvimento local e a infraestrutura na Oracle Cloud Infrastructure (OCI), foram identificadas discrepâncias de versões do motor de orquestração do n8n local (n8n local com versão `1.123.7` enquanto o servidor OCI opera na versão `2.41.3`).

A utilização de tags flutuantes como `:latest` acarreta o risco de quebras silenciosas (*breaking changes*) em nós essenciais (`HTTP Request`, `Aggregate`, `Split Out`) caso caso o container seja recriado. 

Adicionalmente, verificou-se empiricamente que o registry oficial do n8n (`docker.n8n.io` / `dockerhub: n8nio/n8n`) **não disponibiliza tags semânticas parciais** (ex.: `2.41`), resultando no erro `failed to resolve reference ... not found` durante o pull. As imagens são publicadas exclusivamente com o versionamento completo de patch.

---

## 2. Decisão Tomada

Adoção da estratégia de **fixação estrita de versão por patch (Patch Pinning)**, mantendo a flexibilidade de atualização parametrizada via arquivo `.env`:

1. **Definição no Compose:** O serviço no `docker-compose.yml` utiliza interpolação de variáveis apontando para a tag de patch validada em produção:
   ```yaml
   image: n8nio/n8n:${N8N_VERSION:-2.41.3}
   ```
2. **Ponto Único de Configuração:** A versão ativa deve ser sincronizada entre os integrantes do time via variável `N8N_VERSION` no `.env`.

3. **Registry Preferencial:** Utilizar o namespace canônico `n8nio/n8n` do Docker Hub para garantir compatibilidade e resolução de DNS sem intermitências.

---

## 3. Consequências

### 3.1. Prós / Vantagens

- **Paridade de Ambientes:** Garantia de que workflows JSON exportados e validados localmente funcionam de forma idêntica na instância OCI.

- **Previsibilidade Operacional:** Nenhuma atualização de patch ocorre de forma silenciosa ou acidental ao reiniciar os contêiners.

- **Depuração Confiável:** Isola a causa de eventuais anomalias em workflows sem a incerteza de alterações invisíveis de versões no motor.

### 3.2. Contras / Limitações e Riscos Mitigados

- **Atualização Deliberada:** Correções de bugs ou patches de segurança exigem atualização explícita do valor da tag no arquivo `.env` ou `docker-compose.yml` e novo commit no repositório.
