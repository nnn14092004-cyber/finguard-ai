"""Authoritative regulatory knowledge base synthesizer for FinGuard-AI."""

from __future__ import annotations

from pathlib import Path

KNOWLEDGE_BASE_CONTENT = r"""# FINGUARD-AI GLOBAL KNOWLEDGE BASE & REGULATORY BENCHMARKS

## 1. GLOBAL SECURITIES BENCHMARKS & ILLEGAL CAPITAL RAISING
### The Howey Test (U.S. Supreme Court Standard / Global SEC Benchmark)
An instrument or agreement is classified as an **Investment Contract** (Securities) if it meets four cumulative prongs:
1. **Investment of Money:** Exchange of fiat, digital assets, or cryptocurrency.
2. **Common Enterprise:** Pooling of investor funds or horizontal/vertical commonality between promoters and investors.
3. **Expectation of Profits:** Investor expects returns, dividends, capital appreciation, or passive yields.
4. **Derived Solely from the Efforts of Others:** Profits are generated primarily by the promoter, third-party algorithm, or centralized syndicate, with investors remaining entirely passive.
*Violation Trigger:* Any entity offering investment contracts satisfying the Howey Test without registered public prospectus or licensed exemptions from competent regulators (e.g., SEC, FCA, BaFin, MAS, SSC) is conducting unregistered cross-border securities distribution.

---

## 2. PYRAMID SCHEMES & PONZI SCHEME IDENTIFICATION (FTC, IOSCO, OECD)
### FTC Koscot / Amway Test for Pyramid Schemes:
- **Structural Hallmark:** Compensation is paid for the recruitment of other participants rather than the sale of legitimate products or services to ultimate retail consumers.
- **Multi-Tier Referral Structures (MLM Traps):** Multi-level commission structures (Direct bonus, binary leg balancing, generational matching bonuses) applied to capital investment rather than commercial goods.
- **Mandatory Package Purchasing:** Obligation to purchase internal tokens, "mining nodes", "VIP memberships", or "AI licenses" as a prerequisite for earning returns.

### Ponzi Scheme Mechanics:
- **Cash Flow Void:** Absence of genuine underlying economic activity or audited positive cash flow.
- **Substituted Liquidity:** Using incoming capital from subsequent investors to pay returns to earlier participants.
- **Technological Obfuscation:** Masking non-existent revenues behind buzzwords: "Quantum Arbitrage", "AI Predictive High-Frequency Trading", "Defi Liquid Staking Yields".

---

## 3. HIGH-YIELD & FRAUDULENT YIELD BENCHMARKS (FATF & FCA STANDARDS)
### Risk-Return Tradeoff Principles:
- In global financial economics, genuine guaranteed returns cannot fundamentally decouple from the risk-free rate (sovereign bond yields of reserve currencies).
- **Yield Velocity Thresholds:**
  * Fixed guaranteed return > 15% - 20% annualized in USD/fiat without institutional sovereign backing = **High Suspicion**.
  * Guaranteed daily or monthly payouts (e.g., 0.5% - 2% daily, or 5% - 30% monthly) = **100% Certainty of HYIP / Ponzi Architecture**.
- **Psychological Manipulation Patterns:**
  * Absolute safety assertions: "100% Capital Guaranteed", "Zero-Risk Protocol", "Principal Protection Vault".
  * Induced urgency / FOMO: "Exclusive Founder Slots", "Closing in 24 Hours", "Algorithmic Arbitrage Allocation Capped".

---

## 4. CROSS-BORDER CONTRACTUAL TRAPS & UNFAIR TERMS
### Abusive Clauses Under Common Law & Civil Law Doctrines:
1. **Unilateral Modification Right:** The issuer/promoter reserves exclusive rights to amend interest rates, tokenomics, lockup intervals, or withdrawal conditions without explicit investor consent.
2. **Liquidity Locks & Extortionate Exit Barriers:**
   * Mandatory lockup durations exceeding 12 to 36 months for basic capital pools.
   * Punitive early withdrawal penalties stripping 30% to 100% of deposited principal.
   * Conditioned liquidity: Withdrawals require recruiting new participants or achieving network volume quotas.
3. **Jurisdiction Laundering:**
   * Operating internationally while establishing corporate incorporation in non-cooperative secrecy jurisdictions or offshore tax havens (e.g., Seychelles, British Virgin Islands, Marshall Islands, Saint Vincent and the Grenadines) to avoid cross-border law enforcement.
   * Dispute clauses dictating confidential arbitration in remote overseas venues where arbitration filing fees deliberately exceed standard retail claim amounts.
4. **Absolute Liability Disclaimers:** Clauses absolving the issuing company of all legal liability in cases of smart contract failure, system exploits, market volatility, or insolvency.

---

## 5. FINGUARD-AI WEIGHTED RISK SCORING MATRIX
The evaluation engine maps flagged heuristics into an aggregate Suspicion Score ($S$) from 0 to 100:

$$S = \min\left(100, \sum w_i \cdot c_i\right)$$

### Tier 1: Critical Red Flags ($w = +40$ points each)
- Explicit yield guarantees exceeding 30% annualized or any daily/monthly guaranteed yield.
- Multi-tier recruitment commission tied to capital investment pools.
- Operating an unregistered securities offering under the Howey Test.
- Mandating capital routing through anonymous personal crypto wallets without verified escrow.

### Tier 2: High Suspicion ($w = +20$ points each)
- Unilateral modification clause allowing arbitrary policy shifts.
- Capital lockups exceeding 12 months with early exit penalties over 30%.
- Obfuscated revenue generation mechanics relying purely on algorithmic jargon without financial disclosure.

### Tier 3: Cautionary Indicators ($w = +10$ points each)
- Offshore jurisdiction laundering in notorious secrecy havens.
- Coercive FOMO terminology and artificial scarcity tactics.
- Comprehensive disclaimers disavowing all platform fiduciary obligations.

### Output Classification:
- **0 - 24 points: GREEN** -> Standard commercial contract / Negligible scam markers.
- **25 - 49 points: YELLOW** -> Caution advised / Unbalanced clauses requiring legal review.
- **50 - 74 points: ORANGE** -> High Suspicion / Multiple predatory mechanisms identified.
- **75 - 100 points: RED FLAG** -> Critical Hazard / Confirmed Ponzi, illegal pyramid, or financial fraud signatures.
"""


def main() -> None:
    """Writes the canonical regulatory knowledge base to docs directory."""
    project_root = Path(__file__).resolve().parent.parent
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    target_path = docs_dir / "finguard_global_knowledge_base.md"
    target_path.write_text(KNOWLEDGE_BASE_CONTENT.strip() + "\n", encoding="utf-8")

    print(f"SUCCESS: Canonical knowledge base written to: {target_path}")
    print(f"File Size: {target_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
