"""Executive compliance dashboard for financial instrument audits."""

from __future__ import annotations

import pathlib
import sys
from typing import Dict, Tuple

# Ensure repository root is on sys.path for standalone Streamlit execution
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import plotly.graph_objects as go
import streamlit as st

from src.domain.enums import RiskTier
from src.domain.models import AuditAssessmentReport
from src.pipeline import FinGuardPipeline

AUDIT_PRESETS: Dict[str, str] = {
    "Aura Neural Protocol (Multi-Tier Recruitment)": (
        "AURA NEURAL PROTOCOL:\n"
        "Participants deposit capital into our autonomous liquidity allocation matrix.\n"
        "The protocol targets an algorithmic distribution benchmark yielding 150 basis points daily, "
        "backed by autonomous arbitrage with complete insulation from downside principal volatility.\n"
        "No trading expertise is required by passive participants.\n"
        "Earn returns through our multi-tier referral commission structure with downline investment "
        "volume bonuses and a binary bonus on newly recruited capital.\n"
        "Participants must purchase an AI license package to qualify.\n"
        "Mandatory lock-up period of 24 months applies with an early withdrawal penalty of 40%.\n"
        "Withdrawals are conditioned upon active referrals.\n"
        "Governed by the laws of Seychelles, arbitration in Vanuatu."
    ),
    "Synapse Quantum Vault (Guaranteed High Yield)": (
        "SYNAPSE QUANTUM VAULT - PARTICIPATION TERMS\n\n"
        "1. Capital Allocation & Yield:\n"
        "Investors allocate funds into our automated liquidity allocation pool, fully managed by our automated AI neural matrix.\n"
        "Participants remain completely passive and receive a guaranteed 2.5% daily return with 100% capital guaranteed against principal volatility.\n\n"
        "2. Referral Commissions:\n"
        "Members earn multi-tier referral commissions of 15% on level 1 and 5% on level 2 downline investment volume.\n\n"
        "3. Liquidity Terms:\n"
        "A mandatory lock-up period of 18 months applies. Early withdrawal penalty of 40% applies.\n"
        "Management reserves the right to modify terms at any time without prior notice at its sole discretion.\n"
        "This agreement is governed by the laws of Vanuatu."
    ),
    "Howey Passive Syndicate (Unregistered Securities)": (
        "INVESTMENT PARTICIPATION AGREEMENT\n\n"
        "1. Pooling of Capital:\n"
        "Investors provide capital into our collective pooling vault. All trading strategies and asset allocations "
        "are executed entirely by our algorithmic management team.\n\n"
        "2. Passive Entitlement:\n"
        "Participants remain completely passive investors while enjoying regular dividend distributions "
        "derived solely from the proprietary algorithmic trading efforts of the issuer syndicate."
    ),
    "Enterprise Cloud SLA (Commercial Standard)": (
        "ENTERPRISE CLOUD SERVICE LEVEL AGREEMENT (SLA)\n\n"
        "1. Service Commitment:\n"
        "Provider guarantees 99.9% uptime for provisioned compute infrastructure during each monthly billing cycle.\n\n"
        "2. Billing & Invoicing:\n"
        "Customer agrees to remit recurring monthly service fees within thirty (30) days of receipt of invoice.\n\n"
        "3. Termination for Convenience:\n"
        "Either party may terminate this Agreement without cause upon providing sixty (60) days advance written notice.\n\n"
        "4. Governing Law & Dispute Resolution:\n"
        "This instrument is governed by and construed in accordance with the commercial laws of the State of Delaware, United States."
    ),
}

TIER_COLORS = {
    RiskTier.GREEN: "#10B981",
    RiskTier.YELLOW: "#F59E0B",
    RiskTier.ORANGE: "#F97316",
    RiskTier.RED_FLAG: "#EF4444",
}

TIER_BADGES = {
    RiskTier.GREEN: "PASS / LOW RISK",
    RiskTier.YELLOW: "CAUTIONARY REVIEW",
    RiskTier.ORANGE: "HIGH REGULATORY SUSPICION",
    RiskTier.RED_FLAG: "CRITICAL REGULATORY HAZARD",
}


def configure_page_layout() -> None:
    """Configures Streamlit page metadata and layout parameters."""
    st.set_page_config(
        page_title="FinGuard Compliance Auditing Cockpit",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        .metric-card {
            background-color: #1E293B;
            border-radius: 6px;
            padding: 16px 20px;
            border: 1px solid #334155;
            margin-bottom: 12px;
        }
        .metric-label {
            font-size: 0.8rem;
            color: #94A3B8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 2.0rem;
            font-weight: 700;
            margin: 4px 0;
        }
        .verbatim-box {
            background-color: #0F172A;
            border-left: 3px solid #EF4444;
            padding: 10px 14px;
            border-radius: 0 4px 4px 0;
            font-family: monospace;
            color: #F8FAFC;
            margin: 8px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_pipeline() -> FinGuardPipeline:
    """Returns singleton pipeline instance."""
    return FinGuardPipeline()


def render_sidebar() -> Tuple[str, str]:
    """Renders document input controls and scenario selection."""
    st.sidebar.title("FinGuard Engine")
    st.sidebar.caption("Financial Compliance Assessment Interface")
    st.sidebar.markdown("---")

    st.sidebar.subheader("Benchmark Scenarios")
    selected_preset = st.sidebar.selectbox(
        "Select Agreement Template:",
        options=["Custom Document Upload / Text"] + list(AUDIT_PRESETS.keys()),
        index=1,
    )

    st.sidebar.subheader("Document Ingestion")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Agreement (.txt, .md):",
        type=["txt", "md"],
        help="Upload contractual plain text or Markdown agreement.",
    )

    raw_text: str = ""
    file_name: str = "custom_contract.txt"

    if uploaded_file is not None:
        raw_text = uploaded_file.read().decode("utf-8", errors="replace")
        file_name = uploaded_file.name
    elif selected_preset != "Custom Document Upload / Text":
        raw_text = AUDIT_PRESETS[selected_preset]
        file_name = f"{selected_preset.split(' ')[0].lower()}_instrument.txt"
    else:
        raw_text = st.sidebar.text_area(
            "Contract Content:",
            height=200,
            placeholder="Paste contract text for evaluation...",
        )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Codified Frameworks: SEC Howey (1946), FTC Koscot, FATF HYIP Benchmarks, Unfair Terms."
    )

    return raw_text, file_name


def render_executive_metrics(report: AuditAssessmentReport) -> None:
    """Renders high-level audit KPIs."""
    tier_color = TIER_COLORS.get(report.risk_tier, "#94A3B8")
    tier_badge = TIER_BADGES.get(report.risk_tier, str(report.risk_tier.value))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Suspicion Score (S)</div>
                <div class="metric-value" style="color: {tier_color};">{report.suspicion_score} / 100</div>
                <span style="font-size: 0.75rem; color: #94A3B8;">Formula: min(100, sum(w_i * c_i))</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Assigned Risk Tier</div>
                <div class="metric-value" style="color: {tier_color}; font-size: 1.4rem; line-height: 2.0rem;">
                    {report.risk_tier.value}
                </div>
                <span style="font-size: 0.75rem; color: {tier_color}; font-weight: 600;">{tier_badge}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Infractions Flagged</div>
                <div class="metric-value" style="color: #F8FAFC;">{report.total_findings}</div>
                <span style="font-size: 0.75rem; color: #94A3B8;">Heuristic & Semantic Findings</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Remediation Directives</div>
                <div class="metric-value" style="color: #38BDF8;">{len(report.remediation_actions)}</div>
                <span style="font-size: 0.75rem; color: #94A3B8;">Statutory Action Items</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def build_risk_radar_chart(report: AuditAssessmentReport) -> go.Figure:
    """Constructs an institutional 4D polar radar chart for decomposed risk vectors."""
    categories = [
        "Yield Velocity Risk",
        "Structural / MLM Risk",
        "Liquidity Lockup Risk",
        "Legal Jurisdiction Risk",
    ]
    v = report.risk_vector
    values = [
        float(v.yield_risk),
        float(v.structural_risk),
        float(v.liquidity_risk),
        float(v.legal_risk),
    ]

    # Close the radar loop
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    baseline_safe = [25.0, 25.0, 25.0, 25.0, 25.0]

    tier_color = TIER_COLORS.get(report.risk_tier, "#EF4444")
    fill_rgba = (
        "rgba(239, 68, 68, 0.45)"
        if report.risk_tier == RiskTier.RED_FLAG
        else (
            "rgba(249, 115, 22, 0.45)"
            if report.risk_tier == RiskTier.ORANGE
            else (
                "rgba(245, 158, 11, 0.40)"
                if report.risk_tier == RiskTier.YELLOW
                else "rgba(16, 185, 129, 0.35)"
            )
        )
    )

    fig = go.Figure()

    # Statutory Commercial Safe Baseline Envelope (<= 25%)
    fig.add_trace(
        go.Scatterpolar(
            r=baseline_safe,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(16, 185, 129, 0.08)",
            line=dict(color="#10B981", width=1.5, dash="dash"),
            name="Safe Commercial Threshold (<= 25%)",
            hoverinfo="text",
            hovertext="Statutory Baseline Ceiling (25%)",
        )
    )

    # Assessed Contract Risk Polygon
    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor=fill_rgba,
            line=dict(color=tier_color, width=3.0),
            name=f"Assessed Risk Vector ({report.risk_tier.value})",
            hoverinfo="r+theta",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[25, 50, 75, 100],
                ticktext=["25%", "50%", "75%", "100%"],
                tickfont=dict(size=10, color="#94A3B8"),
                gridcolor="#334155",
                linecolor="#475569",
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color="#F1F5F9", family="sans-serif"),
                gridcolor="#334155",
                linecolor="#475569",
            ),
            bgcolor="rgba(15, 23, 42, 0.65)",
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.28,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#CBD5E1"),
        ),
        margin=dict(l=40, r=40, t=25, b=45),
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        height=380,
    )
    return fig


def render_risk_vector_telemetry(report: AuditAssessmentReport) -> None:
    """Renders decomposed orthogonal risk axes with interactive Plotly Radar Chart."""
    st.subheader("Orthogonal Regulatory Risk Decomposition")
    v = report.risk_vector

    radar_col, bar_col = st.columns([1.25, 1.0], gap="large")

    with radar_col:
        radar_fig = build_risk_radar_chart(report)
        st.plotly_chart(radar_fig, use_container_width=True)

    with bar_col:
        st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)

        st.caption("YIELD VELOCITY RISK")
        st.progress(v.yield_risk / 100.0)
        st.write(f"**{v.yield_risk}%** - Guaranteed Yields & FATF HYIP Benchmarks")

        st.caption("STRUCTURAL / MLM RISK")
        st.progress(v.structural_risk / 100.0)
        st.write(f"**{v.structural_risk}%** - SEC Howey Pooling & FTC Koscot Multi-Tier")

        st.caption("LIQUIDITY LOCKUP RISK")
        st.progress(v.liquidity_risk / 100.0)
        st.write(f"**{v.liquidity_risk}%** - Capital Freezes & Exit Penalties")

        st.caption("LEGAL JURISDICTION RISK")
        st.progress(v.legal_risk / 100.0)
        st.write(f"**{v.legal_risk}%** - Offshore Secrecy Venues & Abusive Terms")


def render_audit_details(report: AuditAssessmentReport) -> None:
    """Renders tabs containing itemized findings and remediation actions."""
    st.markdown("---")
    tab_findings, tab_remediation, tab_json = st.tabs(
        ["Clause Findings", "Remediation Directives", "Raw Payload"]
    )

    with tab_findings:
        if not report.findings and not report.semantic_findings:
            st.success("No statutory violations detected. Instrument aligns with standard commercial baselines.")
        else:
            for idx, finding in enumerate(report.findings, start=1):
                rule_id = getattr(finding, "rule_id", "FLAG")
                rule_name = getattr(finding, "rule_name", "Compliance Finding")
                weight = getattr(finding, "weight", 0)
                matched = getattr(finding, "matched_text", "")
                advice = getattr(finding, "remediation_advice", "")
                framework = getattr(finding, "regulatory_framework", "")
                category = getattr(finding, "category", "General")

                with st.expander(f"Finding #{idx}: [{rule_id}] {rule_name} (+{weight} pts)", expanded=True):
                    st.write(f"**Framework:** `{framework}` | **Category:** `{category}`")
                    st.markdown(f'<div class="verbatim-box">"{matched}"</div>', unsafe_allow_html=True)
                    st.write(f"**Remediation Action:** {advice}")

            for idx, sf in enumerate(report.semantic_findings, start=len(report.findings) + 1):
                topic = getattr(sf, "clause_topic", getattr(sf, "category", "Semantic Finding"))
                penalty = getattr(sf, "penalty_weight", getattr(sf, "weight", 20))
                text = getattr(sf, "context_snippet", getattr(sf, "matched_text", ""))
                guidance = getattr(sf, "remediation_guidance", getattr(sf, "remediation_advice", ""))

                with st.expander(f"Finding #{idx}: [SEMANTIC] {topic} (+{penalty} pts)", expanded=True):
                    st.markdown(f'<div class="verbatim-box">"{text}"</div>', unsafe_allow_html=True)
                    st.write(f"**Deception Analysis:** {guidance}")

    with tab_remediation:
        st.subheader("Required Statutory Remediation Actions")
        for idx, action in enumerate(report.remediation_actions, start=1):
            st.markdown(f"**{idx}.** {action}")

    with tab_json:
        st.json(report.model_dump())


def main() -> None:
    """Application entry point."""
    configure_page_layout()
    raw_text, file_name = render_sidebar()

    st.title("FinGuard Compliance Auditing Cockpit")
    st.markdown(
        "Automated regulatory compliance assessment and multi-dimensional risk matrix synthesis for "
        "cross-border investment instruments, syndication agreements, and commercial agreements."
    )

    if not raw_text.strip():
        st.info("Select a preset scenario or supply contract text in the sidebar to run audit.")
        return

    pipeline = get_pipeline()
    report = pipeline.process_document(raw_text=raw_text, file_name=file_name)

    render_executive_metrics(report)
    st.markdown(f"**Executive Verdict:** {report.executive_summary}")
    render_risk_vector_telemetry(report)
    render_audit_details(report)


if __name__ == "__main__":
    main()