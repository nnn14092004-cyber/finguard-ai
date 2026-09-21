# FinGuard-AI: Automated Financial Regulatory Compliance & Contract Risk Audit Pipeline

[![CI Pipeline](https://github.com/nnn14092004/finguard-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/nnn14092004/finguard-ai/actions/workflows/ci.yml)
[![Pytest Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg)](https://github.com/nnn14092004/finguard-ai)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-black.svg)](https://github.com/astral-sh/ruff)
[![Architecture: Clean DDD](https://img.shields.io/badge/Architecture-Domain--Driven-orange.svg)](https://en.wikipedia.org/wiki/Domain-driven_design)

FinGuard-AI is an enterprise-grade financial intelligence engine engineered to automatically ingest, deobfuscate, and audit cross-border investment contracts, multi-tier marketing (MLM) schemes, and high-yield algorithmic solicitations.

The platform maps natural language contractual clauses directly against multilateral regulatory doctrines (SEC Howey Test, FTC Koscot Pyramid Standard, FATF/FCA High-Yield Investment Fraud benchmarks, and Cross-Border Unfair Contract Terms), synthesizing mathematical suspicion metrics and a decomposed four-dimensional risk vector.

---

## 1. Executive System Architecture

FinGuard-AI enforces Clean Architecture and Domain-Driven Design (DDD) principles. The ingestion pipeline separates concerns across deterministic heuristic pattern scanning, contextual NLP auditing, mathematical risk synthesis, and multi-interface presentation.

```mermaid
graph TD
    subgraph Ingestion_Layer [Ingestion & Normalization Layer]
        A[Inbound Document: PDF / TXT / Markdown] --> B[TextNormalizer Engine]
        B -->|Unicode NFKC & Spacing Deobfuscation| C[DocumentPayload Model]
    end

    subgraph Inspection_Layer [Multilateral Inspection Engines]
        C --> D[HeuristicScanner: Regex Pattern Catalog]
        C --> E[SemanticAuditor: NLP Contextual Disguise Engine]
    end

    subgraph Scoring_Layer [Mathematical Risk Synthesis]
        D -->|Clause Findings: Weights w_i| F[ScoringEngine Matrix]
        E -->|Semantic Risk Penalties| F
        F -->|S = min 100, sum w_i c_i| G[AuditAssessmentReport Domain Entity]
        F -->|Decompose 4D Coordinates| H[MultiDimensionalRiskVector]
    end

    subgraph Delivery_Layer [Enterprise Delivery Interfaces]
        G --> I[FastAPI REST Gateway :8000]
        G --> J[Streamlit Executive Dashboard :8501]
        G --> K[Batch Auditor CLI Harness]
    end