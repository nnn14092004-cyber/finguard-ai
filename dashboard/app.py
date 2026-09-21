"""Interactive FinTech Audit Dashboard for FinGuard-AI (Phase 4).

Provides real-time document analysis, multi-dimensional risk radar charts,
verbatim predatory clause inspection, and regulatory remediation actions.
"""

from __future__ import annotations

import sys
from pathlib import Path

# =============================================================================
# Architectural Bootstrap: Ensure Project Root is in sys.path
# =============================================================================
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import plotly.graph_objects as go
import streamlit as st

from src.domain.enums import RiskTier
from src.pipeline import FinGuardPipeline

# Configure Streamlit page layout
st.set_page_config(
    page_title="FinGuard-AI | Enterprise Risk Audit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_pipeline() -> FinGuardPipeline:
    """Initializes and caches the master FinGuard audit pipeline."""
    return FinGuardPipeline()


pipeline = get_pipeline()

# Header Section
st.title("🛡️ FinGuard-AI: Predatory Contract Audit System")
st.markdown(
    "**Automated Financial Intelligence Gateway:** Unmasking high-yield Ponzi mechanisms, "
    "unregistered securities distribution (SEC Howey), MLM recruitment traps (FTC Koscot), "
    "and cross-border jurisdiction laundering."
)
st.divider()

# Sidebar: Configuration & Preloaded Test Cases
st.sidebar.header("📁 Document Ingestion")
sample_choice = st.sidebar.selectbox(
    "Load Synthetic Regulatory Test Case:",
    [
        "Custom Input",
        "Aura Neural Protocol (Veiled HYIP & Pyramid)",
        "Legitimate Cloud Enterprise SLA (Low Risk)",
    ],
)

sample_aura = """AURA NEURAL PROTOCOL - PRIVATE PLACEMENT MEMORANDUM

1. Capital Allocation & Yield Mechanics:
Participants deposit capital into our autonomous liquidity allocation matrix.
The protocol targets an algorithmic distribution benchmark yielding 150 basis points daily,
backed by autonomous arbitrage with complete insulation from downside principal volatility.
No trading expertise is required by passive participants.

2. Affiliate Incentives & Tier Membership:
Earn exceptional returns through our multi-tier referral commission structure.
Receive downline investment volume bonuses and a binary bonus on newly recruited capital.
Participants must purchase an AI license package to qualify for high-tier incentives.

3. Liquidity & Capital Preservation:
All allocated funds are subject to a mandatory lock-up period of 24 months.
In the event of early liquidation, an early withdrawal penalty of 40% will be assessed.
Withdrawals are conditioned upon maintaining active downline referral nodes.

4. Governing Law & Arbitration:
The issuer reserves the right to modify these terms, interest rates, and withdrawal rules
at any time without prior notice.
This agreement is strictly governed by the laws of Seychelles.
All disputes shall be resolved solely via arbitration in Vanuatu.
"""

sample_saas = """ENTERPRISE CLOUD SERVICE LEVEL AGREEMENT (SLA)

1. Services: Provider grants access to managed relational database clusters with 99.9% uptime.
2. Fees & Billing: Recurring monthly subscription fees are invoiced based on provisioned RAM and storage.
3. Termination: Either party may terminate with 30 days prior written notice. Unused prepaid balances refunded.
4. Jurisdiction: This commercial agreement is governed by the laws of the State of Delaware, United States.
"""

default_text = ""
if sample_choice == "Aura Neural Protocol (Veiled HYIP & Pyramid)":
    default_text = sample_aura
elif sample_choice == "Legitimate Cloud Enterprise SLA (Low Risk)":
    default_text = sample_saas

uploaded_file = st.sidebar.file_uploader(
    "Or upload contract text file (.txt, .md):",
    type=["txt", "md"],
)

if uploaded_file is not None:
    contract_text = uploaded_file.read().decode("utf-8", errors="replace")
    doc_name = uploaded_file.name
else:
    contract_text = st.text_area(
        "Input Agreement / Financial Promotion Text:",
        value=default_text,
        height=260,
        placeholder="Paste full terms of service, participation agreement, or promotional text here...",
    )
    doc_name = "analyzed_contract.txt"

run_audit_btn = st.button("🚀 Execute Comprehensive Regulatory Audit", type="primary")

if run_audit_btn and contract_text.strip():
    with st.spinner("Analyzing text across FATF, SEC Howey, and FTC benchmarks..."):
        report = pipeline.process_document(contract_text, file_name=doc_name)

    # 1. Top Metrics Dashboard
    col_score, col_tier, col_flags, col_breakdown = st.columns(4)

    tier_colors = {
        RiskTier.GREEN: "green",
        RiskTier.YELLOW: "goldenrod",
        RiskTier.ORANGE: "darkorange",
        RiskTier.RED_FLAG: "red",
    }
    tier_color = tier_colors.get(report.risk_tier, "red")

    col_score.metric("Suspicion Score", f"{report.suspicion_score} / 100")
    col_tier.markdown(
        f"**Risk Tier Classification:**<br><span style='font-size: 26px; font-weight: bold; color: {tier_color};'>"
        f"{report.risk_tier.value}</span>",
        unsafe_allow_html=True,
    )
    col_flags.metric("Flagged Violations", f"{report.total_findings}")
    col_breakdown.markdown(
        f"**Severity Distribution:**<br>"
        f"🔴 Tier 1 Critical: **{report.scoring_breakdown.tier_1_critical_count}**<br>"
        f"🟠 Tier 2 High: **{report.scoring_breakdown.tier_2_high_count}**<br>"
        f"🟡 Tier 3 Cautionary: **{report.scoring_breakdown.tier_3_cautionary_count}**",
        unsafe_allow_html=True,
    )

    st.divider()

    # 2. Multi-Dimensional Risk Radar Chart & Executive Summary
    col_viz, col_summary = st.columns([1, 1])

    with col_viz:
        st.subheader("📊 Multi-Dimensional Risk Decomposition")
        categories = [
            "Yield Deception<br>(FATF/FCA)",
            "Structural & Pyramid<br>(SEC/FTC)",
            "Liquidity Lockup<br>(Unfair Terms)",
            "Legal & Jurisdiction<br>(Offshore)",
        ]
        values = [
            report.risk_vector.yield_risk,
            report.risk_vector.structural_risk,
            report.risk_vector.liquidity_risk,
            report.risk_vector.legal_risk,
        ]
        # Close radar loop
        categories.append(categories[0])
        values.append(values[0])

        fig = go.Figure(
            data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                fillcolor="rgba(255, 65, 54, 0.3)" if report.suspicion_score >= 75 else "rgba(46, 204, 64, 0.3)",
                line=dict(color="#FF4136" if report.suspicion_score >= 75 else "#2ECC40", width=2),
            )
        )
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(l=40, r=40, t=30, b=30),
            height=340,
        )
        st.plotly_chart(fig, width="stretch")

    with col_summary:
        st.subheader("📑 Executive Compliance Summary")
        if report.risk_tier == RiskTier.RED_FLAG:
            st.error(report.executive_summary)
        elif report.risk_tier == RiskTier.ORANGE:
            st.warning(report.executive_summary)
        elif report.risk_tier == RiskTier.YELLOW:
            st.info(report.executive_summary)
        else:
            st.success(report.executive_summary)

        st.markdown(f"**Document Tracking UUID:** `{report.document_id}`")
        st.markdown(f"**Total Findings Detected:** `{report.total_findings}`")

    st.divider()

    # 3. Deep Contextual Semantic Findings (Phase 3)
    if report.semantic_findings:
        st.subheader("🧠 Deep NLP Contextual Findings (Semantic Audit)")
        for idx, item in enumerate(report.semantic_findings, start=1):
            with st.expander(
                f"🔍 Semantic Finding {idx}: {item.clause_topic} (Confidence: {item.confidence_score * 100:.1f}%)",
                expanded=True,
            ):
                st.markdown(f"**Flagged Passage:** *\"{item.extracted_text}\"*")
                st.markdown(f"**Deceptive Mechanism:** {item.deceptive_intent}")
                st.caption(f"Benchmark Reference: {item.regulatory_relevance.value}")

    # 4. Deterministic Heuristic Violations (Phase 1 & 2)
    st.subheader("⚖️ Flagged Contractual Clauses & Regulatory Doctrines")
    if report.findings:
        for idx, finding in enumerate(report.findings, start=1):
            with st.expander(f"[{idx}] {finding.rule_id} - {finding.rule_name} (Weight: +{finding.weight}) [{finding.category}]"):
                st.markdown(f"**Verbatim Contract Text:**")
                st.code(finding.matched_text, language="text")
                st.markdown(f"**Governing Framework:** `{finding.regulatory_framework.value}`")
                st.markdown(f"**Remediation Countermeasure:** {finding.remediation_advice}")
    else:
        st.success("No predatory clauses detected across active regulatory catalogs.")

    st.divider()

    # 5. Prioritized Remediation Actions & Export
    st.subheader("🛡️ Prioritized Actionable Recourse Steps")
    for idx, action in enumerate(report.remediation_actions, start=1):
        st.markdown(f"**{idx}.** {action}")

    st.divider()
    st.download_button(
        label="📥 Download Official JSON Audit Report",
        data=report.model_dump_json(indent=2),
        file_name=f"finguard_audit_{report.document_id[:8]}.json",
        mime="application/json",
    )