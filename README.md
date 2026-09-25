# FinGuard-AI: Regulatory Contract Audit Engine

[![tests](https://img.shields.io/badge/tests-37%2F37%20passing-brightgreen)](https://github.com/nnn14092004-cyber/finguard-ai/actions)
[![coverage](https://img.shields.io/badge/coverage-83.86%25-brightgreen)](https://github.com/nnn14092004-cyber/finguard-ai)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

FinGuard-AI reads financial contracts, PPMs, and syndication agreements and
flags patterns tied to unregistered securities, Ponzi/MLM structuring, and
predatory yield terms. It's meant as a fast first-pass triage before a document
reaches a compliance officer or outside counsel -- not a replacement for
either.

The core motivation: manual review is slow (hours to days per agreement) and
keyword filters are trivially bypassed with things like cross-line hyphenation
or euphemistic phrasing. FinGuard-AI leans on a deterministic rule engine
first, with a semantic layer as fallback, rather than routing everything
through an LLM that could hallucinate a finding with no way to audit why.

## 1. What it checks for

The rule catalog covers four areas, each mapped to a real regulatory
framework:

* **Howey Doctrine (15 U.S.C. §77e / SEC v. Howey)** -- the four-prong test for
  an unregistered investment contract: investment of money, common enterprise,
  expectation of profit, and profit derived from a third party's effort.
* **FTC Koscot / anti-pyramid standards** -- compensation structures driven by
  recruiting new participants rather than a real product, binary/matrix
  bonuses, mandatory "starter package" purchases.
* **FATF/FCA HYIP & AML standards** -- yields decoupled from any real
  risk-free rate, "100% guaranteed / zero risk" language, and routing investor
  funds through unverified wallets or bots (a Travel Rule red flag).
* **Cross-border unfair terms / UDAAP** -- long capital lockups, punitive
  early-withdrawal penalties, unilateral contract amendment rights, and
  offshore forum-shopping to non-cooperative jurisdictions.

## 2. Scoring

Findings roll up into a single Suspicion Score (0-100), plus a 4D risk vector
so a single number doesn't hide *why* something scored high:

* **Yield Velocity Risk** -- unsustainable/guaranteed-return claims
* **Structural / MLM Risk** -- recruitment-driven compensation
* **Liquidity Lockup Risk** -- withdrawal restrictions, redemption gates
* **Legal Jurisdiction Risk** -- unilateral terms, offshore forum evasion

| Tier | Score | Meaning |
|---|---|---|
| GREEN | 0-24 | Standard commercial contract, no material flags |
| YELLOW | 25-49 | Non-standard covenants, worth a legal look |
| ORANGE | 50-74 | Predatory patterns present (lockups, offshore venues, unilateral terms) |
| RED | 75-100 | Strong indicators of an unregistered security, Ponzi structure, or pyramid |

## 3. Architecture

Three layers, kept deliberately decoupled so a non-deterministic component
(the semantic fallback) can never corrupt a deterministic one:

```text
1. Ingestion
   Raw text / PDF -> pypdf extraction (in-memory) -> Unicode NFKC
   normalization + cross-line dehyphenation

2. Inspection core
   HeuristicScanner (15 codified regex rules, deterministic)
       + SemanticAuditor (LLM fallback for phrasing the regex misses)
   -> ScoringEngine (4D vector + SHA-256 provenance hash)

3. Delivery
   AuditAssessmentReport (Pydantic schema)
       -> FastAPI REST endpoint (/api/v1/audit/text, /file)
       -> Streamlit dashboard (radar chart + summary)
       -> PDF dossier export
```

Every ingested document gets SHA-256 hashed at normalization time, and that
hash gets stamped into the report metadata and the PDF dossier header/footer --
so if the source text changes even slightly, the audit no longer matches. That
part is a design property, not a legal certification; see Section 7 for what
this doesn't claim.

## 4. What I've actually measured

Everything below is from real runs on my dev machine
(`scripts/run_final_acceptance.py`, which chains all of these), not
invented numbers. Full raw output, including per-file results, is in
`benchmark_results.json` after running the benchmark yourself.

### 4.1 Test suite

37/37 tests passing, 83.86% coverage (`pytest --cov=src`). Also passing:
`ruff check`, `ruff format --check`, and `mypy --strict` across the whole
`src/` tree.

### 4.2 100-document adversarial benchmark

Run against a synthetic corpus the project generates itself
(`data/benchmark/`) -- 80 documents with predatory clauses deliberately
embedded in realistic boilerplate (including obfuscation like cross-line
hyphens), and 20 clean commercial contracts as negative controls:

| Metric | Result |
|---|---|
| True Positives | 80 / 80 |
| True Negatives | 20 / 20 |
| False Positives | 0 / 20 |
| False Negatives | 0 / 80 |
| Recall | 100.00% |
| Precision | 100.00% |
| Average latency / doc | 6.87 ms |
| P95 latency | 7.60 ms |
| Total time (100 docs) | 0.69 s |

Worth being upfront about what this does and doesn't prove: it's a perfect
score on a benchmark the project itself generated, with known patterns it was
built to catch. It's a solid regression check, not independent third-party
validation. If a document uses obfuscation this rule set wasn't designed for,
this benchmark won't tell you that.

### 4.3 Historical case backtest

Five real, publicly documented cases run through `test_historical_cases.py`:

| Case | Expected | Result | Score | Latency | Rules triggered |
|---|---|---|---|---|---|
| BitConnect | RED | RED | 100/100 | 2.99 ms | 8 (AML-001, HOWEY-001, HYIP-001, LOCK-001, LOCK-002, MLM-001, PYR-001, PYRAMID-001) |
| ZeekRewards | RED | RED | 100/100 | 1.85 ms | 5 |
| Madoff / BLMIS | RED | RED | 80/100 | 1.73 ms | 3 |
| Anchor Protocol / Terra | RED | RED | 100/100 | 1.71 ms | 5 |
| NVCA Series A (clean control) | GREEN | GREEN | 0/100 | 2.18 ms | 0 |

All 5 matched their expected tier. Note: the BitConnect numbers here (2.99ms,
8 rule categories) come from this backtest script, which is different from
the interactive Streamlit dashboard run shown elsewhere in this repo's
history (7.27ms, 23 flagged occurrences) -- the dashboard adds its own UI
overhead and counts individual rule *occurrences* rather than distinct rule
*categories*. Same underlying engine, two different measurement contexts.

### 4.4 Component-level latency

From `profile_engine_latency.py`:

| Component | p50 | p95 | p99 |
|---|---|---|---|
| TextNormalizer | 0.066 ms | 0.081 ms | 0.113 ms |
| HeuristicScanner (15 rules) | 0.472 ms | 0.723 ms | 0.891 ms |
| ScoringEngine | 0.010 ms | 0.010 ms | 0.013 ms |
| PDF dossier generation | 24.4 ms | 32.0 ms | 35.8 ms |
| Full pipeline (E2E) | 0.609 ms | 0.786 ms | 0.974 ms |

The PDF export is the slow part by a wide margin (ReportLab rendering), but
it's not on the audit hot path -- scoring itself finishes in under a
millisecond.

## 5. Setup

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

Run everything at once:
```bash
python scripts/run_final_acceptance.py
```
This chains lint + type-check + pytest + historical backtest + 100-doc
benchmark + latency profiling. Takes about 20-25 seconds on my machine.

Or run pieces individually:
```bash
pytest -v --tb=short --cov=src tests/
python scripts/test_historical_cases.py
python scripts/run_benchmark.py
python scripts/profile_engine_latency.py
```

Launch the services:
```bash
# Terminal 1 -- API
uvicorn src.api.app:app --host 127.0.0.1 --port 8000 --reload
# http://127.0.0.1:8000/docs

# Terminal 2 -- dashboard
streamlit run src/ui/dashboard.py --server.port 8501
# http://127.0.0.1:8501
```

Or via Docker:
```bash
docker compose build --no-cache
docker compose up -d
```

## 6. Project layout

```text
finguard-ai/
├── data/benchmark/          synthetic adversarial test corpus + ground truth
├── data/historical_cases/   real fraud case documents used in backtesting
├── docs/                    regulatory knowledge base, sample dossiers
├── scripts/                 test runners, benchmark generators, acceptance harness
├── src/
│   ├── api/                 FastAPI gateway
│   ├── domain/               models, enums
│   ├── engines/              heuristic scanner, semantic auditor, scoring engine
│   ├── ingestion/            PDF extraction + normalization
│   ├── reporting/            PDF dossier generator
│   ├── rules/                the 15-rule catalog
│   ├── ui/                   Streamlit dashboard
│   └── pipeline.py           orchestration facade
└── tests/
```

## 7. What this doesn't claim

This is a working prototype, tested against its own benchmark and a small set
of historical cases -- not an audited compliance product, and not a
substitute for legal review. It hasn't been reviewed by anyone outside this
project, and the 100% recall/precision numbers above are against a
self-generated benchmark, not an independent one. The SHA-256 provenance
hashing is a real, useful integrity property (any edit to the source
document invalidates the hash), but calling a PDF "court-admissible" is a
legal determination for a court to make, not something software can assert
about itself.

## Roadmap

- [ ] Independent/adversarial benchmark built by someone other than the
      project author
- [ ] Expand the historical case corpus beyond 5 cases
- [ ] Third-party review of the rule catalog against current case law
- [ ] Confidence intervals or explainability output alongside the raw score

## License

MIT
