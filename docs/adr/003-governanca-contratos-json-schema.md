# ADR-003: Governança de Contratos de Dados com JSON Schema Canónico

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

O pipeline de dados recolhe publicações e interações a partir de múltiplas fontes públicas com estruturas heterogêneas (Stack Exchange API, Mastodon API e Hacker News via Algolia). Cada plataforma apresenta convenções distintas de nomenclatura, campos opcionais, remoção de utilizadores e estruturas de metadados.

Para além disso, a arquitetura prevê etapas de enriquecimento analítico via DuckDB e revisão humana (HITL - Human-in-the-Loop) através de uma interface em Streamlit antes da persistência final no OCI Object Storage. 

Sem contratos de dados formais, falhas estruturais só seriam detectadas tardiamente na persistência ou na renderização da interface visual.

---

## 2. Decisão Tomada

Implementar uma estratégia de **contratos canônicos de dados utilizando JSON Schema**, dividida em duas fronteiras de validação estritas:

1. **`schemas/input_schema.json` (Fronteira de Ingestão):**
   - Valida os dados brutos padronizados após a saída dos nós do n8n e antes da carga no DuckDB.

   - Exige chaves fundamentais (`source_id`, `creation_date`) e padroniza a ausência de metadados com valores nulos explícitos (`null`), eliminando dados literais arbitrários como `"Anonymous"`.

2. **`schemas/output_schema.json` (Fronteira de Entrega / HITL):**
   - Valida o pacote de dados final consolidado e aprovado através da aplicação Streamlit antes da escrita definitiva nos buckets do OCI Object Storage.

3. **Isolamento de Código (`src/validation/`):**
   - A lógica de validação programática (ex.: via biblioteca `jsonschema` em Python) fica isolada na pasta dedicada `src/validation/`, separada das visualizações (`src/views/`) e da infraestrutura (`src/services/`).

---

## 3. Consequências

### 3.1. Prós / Vantagens

- **Desacoplamento Técnico:** O coletor (n8n), as transformações analíticas (DuckDB) e o frontend (Streamlit) comunicam via contratos explícitos e auditáveis.

- **Deteção Precoce de Falhas:** Alterações em APIs de terceiros que quebrem contratos são barradas logo na camada de validação inicial.

- **Integridade SQL no DuckDB:** A garantia de campos nulos reais (`null`) assegura métricas corretas de agregação (`COUNT(DISTINCT ...)`) sem poluição analítica.

### 3.2. Contras / Limitações e Riscos Mitigados

- Qualquer adição ou remoção de campos no pipeline requer a abertura de um Pull Request com atualização formal e sincronizada dos arquivos em `schemas/`.
