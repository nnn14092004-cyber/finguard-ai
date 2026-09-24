"""Institutional compliance auditing cockpit and risk telemetry interface."""

from __future__ import annotations

import pathlib
import sys
import time

# Ensure repository root is discoverable on sys.path
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import plotly.graph_objects as go
import streamlit as st

from src.domain.enums import RegulatoryFramework, RiskTier, Severity
from src.domain.models import AuditAssessmentReport
from src.ingestion.normalizer import extract_text_from_pdf
from src.pipeline import FinGuardPipeline
from src.reporting.pdf_generator import ForensicReportGenerator

AUDIT_PRESETS: dict[str, str] = {
    "Aura Neural Protocol (Multi-Tier Recruitment Trap)": (
        "AURA NEURAL PROTOCOL - CONFIDENTIAL OFFERING MEMORANDUM\n"
        "1. Capital Deployment & Target Yield:\n"
        "Participants deposit digital assets into our autonomous algorithmic liquidity allocation matrix. "
        "The protocol targets an algorithmic distribution benchmark yielding 150 basis points daily, "
        "backed by autonomous arbitrage with complete insulation from downside principal volatility.\n"
        "2. Passive Participation & Management:\n"
        "No trading expertise is required by passive participants. All execution is handled entirely "
        "by our specialized quantitative algorithmic team.\n"
        "3. Network Incentives & Multi-Tier Compensation:\n"
        "Participants earn revenue through our multi-tier referral commission structure with downline investment "
        "volume bonuses and a binary bonus on newly recruited capital. Participants must purchase an AI license package to qualify.\n"
        "4. Liquidity Terms & Jurisdiction:\n"
        "Mandatory lock-up period of 24 months applies with an early withdrawal penalty of 40%. "
        "Withdrawals are conditioned upon maintaining active referrals. "
        "This instrument is governed by the laws of Seychelles, with mandatory confidential arbitration in Vanuatu."
    ),
    "Synapse Quantum Vault (Guaranteed Yield & Unhosted Wallets)": (
        "SYNAPSE QUANTUM VAULT - PARTICIPATION TERMS\n\n"
        "1. Capital Allocation & Yield:\n"
        "Investors allocate funds into our automated liquidity allocation pool, fully managed by our automated neural matrix.\n"
        "Participants remain completely passive and receive a guaranteed 2.5% daily return with 100% capital guaranteed against principal volatility.\n\n"
        "2. Referral Commissions & Routing:\n"
        "Members earn multi-tier referral commissions of 15% on level 1 and 5% on level 2 downline investment volume.\n"
        "Participants deposit capital directly to anonymous personal crypto wallet without KYC.\n\n"
        "3. Liquidity Terms & Discretion:\n"
        "A mandatory lock-up period of 18 months applies. Early withdrawal penalty fee strips 40% of initial principal.\n"
        "Management reserves the right to modify terms at any time without prior notice at its sole discretion.\n"
        "This agreement is governed by the laws of Vanuatu."
    ),
    "Series A Preferred Stock (Standard Commercial Baseline)": (
        "SERIES A PREFERRED SHAREHOLDERS AGREEMENT:\n"
        "1. Founder Equity Lock-up: Founders agree to a standard founder share lock-up following "
        "the execution of this Agreement, subject to a four-year linear vesting schedule with a one-year cliff.\n"
        "2. Transfer Restrictions: No Shareholder shall transfer, pledge, or encumber common stock without "
        "prior written consent of the Board of Directors representing a qualified corporate majority.\n"
        "3. Applicable Jurisdiction: Governed in accordance with the laws of the State of Delaware, United States."
    ),
    "Enterprise Software Service Agreement (Negative Control)": (
        "MASTER ENTERPRISE SOFTWARE SUBSCRIPTION AGREEMENT:\n"
        "1. Service Availability: Provider shall maintain monthly system availability of at least 99.9%.\n"
        "2. Tiered Platform License: Customer is licensed for up to 500 concurrent administrative seats.\n"
        "3. Bilateral Termination: Either party may terminate upon 30 days written notice for uncured material breach.\n"
        "4. Governing Law: This Agreement is governed by the commercial laws of England and Wales."
    ),
}

TIER_COLORS = {
    RiskTier.GREEN: "#10b981",
    RiskTier.YELLOW: "#f59e0b",
    RiskTier.ORANGE: "#f97316",
    RiskTier.RED_FLAG: "#ef4444",
}

TIER_DESCRIPTIONS = {
    RiskTier.GREEN: "COMMERCIAL BASELINE (LOW RISK)",
    RiskTier.YELLOW: "CAUTIONARY REVIEW REQUIRED",
    RiskTier.ORANGE: "HIGH REGULATORY SUSPICION",
    RiskTier.RED_FLAG: "CRITICAL REGULATORY HAZARD",
}


def configure_page_layout() -> None:
    """Configures application metadata and institutional stylesheet."""
    st.set_page_config(
        page_title="FinGuard-AI Compliance Auditing Cockpit",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        .main {
            background-color: #0b0f19;
        }
        .metric-card {
            background-color: #151d30;
            border-radius: 6px;
            padding: 14px 18px;
            border: 1px solid #1e293b;
            margin-bottom: 12px;
        }
        .metric-label {
            font-size: 0.75rem;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin: 4px 0;
            font-family: 'Courier New', monospace;
        }
        .metric-caption {
            font-size: 0.75rem;
            color: #64748b;
        }
        .tier-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        .badge-green { background-color: #064e3b; color: #34d399; border: 1px solid #059669; }
        .badge-yellow { background-color: #713f12; color: #fde047; border: 1px solid #ca8a04; }
        .badge-orange { background-color: #7c2d12; color: #fdba74; border: 1px solid #ea580c; }
        .badge-red { background-color: #7f1d1d; color: #fca5a5; border: 1px solid #dc2626; }
        .evidence-quote-box {
            background-color: #0f172a;
            border-left: 3px solid #ef4444;
            padding: 10px 14px;
            border-radius: 0 4px 4px 0;
            font-family: monospace;
            font-size: 0.85rem;
            color: #f1f5f9;
            margin: 8px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_pipeline() -> FinGuardPipeline:
    """Initializes and returns cached pipeline instance."""
    return FinGuardPipeline()


@st.cache_resource
def get_report_generator() -> ForensicReportGenerator:
    """Initializes and returns cached forensic PDF dossier generator."""
    return ForensicReportGenerator()


def build_risk_radar_chart(report: AuditAssessmentReport) -> go.Figure:
    """Constructs a 4D polar radar chart mapping decomposed contractual exposure."""
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

    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    baseline_safe = [25.0, 25.0, 25.0, 25.0, 25.0]

    tier_color = TIER_COLORS.get(report.risk_tier, "#ef4444")
    fill_rgba = (
        "rgba(239, 68, 68, 0.35)"
        if report.risk_tier == RiskTier.RED_FLAG
        else (
            "rgba(249, 115, 22, 0.35)"
            if report.risk_tier == RiskTier.ORANGE
            else (
                "rgba(245, 158, 11, 0.30)"
                if report.risk_tier == RiskTier.YELLOW
                else "rgba(16, 185, 129, 0.25)"
            )
        )
    )

    fig = go.Figure()

    # Commercial Baseline Envelope (Safe Threshold <= 25%)
    fig.add_trace(
        go.Scatterpolar(
            r=baseline_safe,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(16, 185, 129, 0.05)",
            line=dict(color="#10b981", width=1.5, dash="dash"),
            name="Commercial Baseline Ceiling (25%)",
            hoverinfo="text",
            hovertext="Safe Commercial Threshold (<= 25%)",
        )
    )

    # Assessed Contract Risk Vector
    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor=fill_rgba,
            line=dict(color=tier_color, width=2.5),
            marker=dict(size=6, color=tier_color),
            name=f"Assessed Exposure ({report.risk_tier.value})",
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
                tickfont=dict(size=9, color="#64748b"),
                gridcolor="#1e293b",
                linecolor="#334155",
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color="#cbd5e1", family="sans-serif"),
                gridcolor="#1e293b",
                linecolor="#334155",
            ),
            bgcolor="rgba(15, 23, 42, 0.4)",
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color="#94a3b8"),
        ),
        margin=dict(l=40, r=40, t=20, b=40),
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        height=320,
    )
    return fig


def render_sidebar() -> tuple[str, str]:
    """Renders document input controls and scenario templates."""
    st.sidebar.title("FinGuard-AI Engine")
    st.sidebar.caption("Regulatory Compliance Examination Interface")
    st.sidebar.markdown("---")

    st.sidebar.subheader("Document Presets")
    selected_preset = st.sidebar.selectbox(
        "Institutional Benchmark Scenarios:",
        options=["Custom Document Ingestion"] + list(AUDIT_PRESETS.keys()),
        index=1,
    )

    st.sidebar.subheader("File Ingestion")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Agreement (.pdf, .txt, .md):",
        type=["pdf", "txt", "md"],
        help="In-memory extraction pipeline with zero persistent disk footprint.",
    )

    raw_text: str = ""
    file_name: str = "custom_contract.txt"

    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_bytes = uploaded_file.read()
        if file_name.lower().endswith(".pdf"):
            with st.spinner("Extracting text streams from PDF..."):
                try:
                    raw_text = extract_text_from_pdf(file_bytes)
                except Exception as exc:
                    st.sidebar.error(f"PDF extraction error: {exc}")
        else:
            raw_text = file_bytes.decode("utf-8", errors="replace")
    elif selected_preset != "Custom Document Ingestion":
        raw_text = AUDIT_PRESETS[selected_preset]
        file_name = f"{selected_preset.split(' ')[0].lower()}_agreement.txt"

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Governing Frameworks")
    st.sidebar.caption(
        "Pillar I: SEC Howey Doctrine (15 U.S.C. 77e)\n\n"
        "Pillar II: FTC Koscot & Amway Standards\n\n"
        "Pillar III: FATF & FCA High-Yield Standards\n\n"
        "Pillar IV: Cross-Border Unfair Contract Terms"
    )

    return raw_text, file_name


def render_telemetry_kpis(report: AuditAssessmentReport, latency_ms: float) -> None:
    """Renders primary regulatory metrics in institutional KPI format."""
    tier = report.risk_tier
    tier_color = TIER_COLORS.get(tier, "#94a3b8")
    badge_class = {
        RiskTier.GREEN: "badge-green",
        RiskTier.YELLOW: "badge-yellow",
        RiskTier.ORANGE: "badge-orange",
        RiskTier.RED_FLAG: "badge-red",
    }.get(tier, "badge-red")
    tier_desc = TIER_DESCRIPTIONS.get(tier, tier.value)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="tier-badge {badge_class}">{tier.value}</div>
                <div class="metric-label">Suspicion Score (S)</div>
                <div class="metric-value" style="color: {tier_color};">{report.suspicion_score} / 100</div>
                <div class="metric-caption">{tier_desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Infractions Flagged</div>
                <div class="metric-value" style="color: #f8fafc;">{report.total_findings}</div>
                <div class="metric-caption">Deterministic & Semantic Findings</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Processing Latency</div>
                <div class="metric-value" style="color: #38bdf8;">{latency_ms:.2f} ms</div>
                <div class="metric-caption">Sub-Second Execution SLA</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Remediation Directives</div>
                <div class="metric-value" style="color: #a78bfa;">{len(report.remediation_actions)}</div>
                <div class="metric-caption">Actionable Compliance Items</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_findings_tab(report: AuditAssessmentReport) -> None:
    """Renders itemized legal infractions and evidentiary text snippets."""
    if not report.findings and not report.semantic_findings:
        st.success(
            "Zero statutory violations detected. Instrument aligns with standard commercial contracting baselines."
        )
        return

    for idx, finding in enumerate(report.findings, start=1):
        rule_id = getattr(finding, "rule_id", "RULE")
        rule_name = getattr(finding, "rule_name", "Statutory Infraction")
        weight = getattr(finding, "weight", 0)
        matched_text = getattr(finding, "matched_text", "")
        remediation = getattr(finding, "remediation_advice", "")
        framework = getattr(finding, "regulatory_framework", "")
        framework_val = (
            framework.value if isinstance(framework, RegulatoryFramework) else str(framework)
        )

        severity = getattr(finding, "severity", "")
        severity_val = severity.value if isinstance(severity, Severity) else str(severity)

        with st.expander(
            f"Infraction #{idx}: [{rule_id}] {rule_name} (+{weight} pts)",
            expanded=True,
        ):
            meta_col1, meta_col2 = st.columns([1, 1])
            with meta_col1:
                st.write(f"**Regulatory Framework:** `{framework_val}`")
            with meta_col2:
                st.write(f"**Statutory Severity:** `{severity_val}`")

            st.markdown(
                f'<div class="evidence-quote-box">"{matched_text}"</div>',
                unsafe_allow_html=True,
            )
            st.write(f"**Prescribed Remediation:** {remediation}")

    for idx, sf in enumerate(report.semantic_findings, start=len(report.findings) + 1):
        topic = getattr(sf, "clause_topic", getattr(sf, "category", "Semantic Infraction"))
        penalty = getattr(sf, "penalty_weight", getattr(sf, "weight", 20))
        extracted = getattr(
            sf, "context_snippet", getattr(sf, "extracted_text", getattr(sf, "matched_text", ""))
        )
        guidance = getattr(sf, "remediation_guidance", getattr(sf, "remediation_advice", ""))

        with st.expander(
            f"Infraction #{idx}: [SEMANTIC] {topic} (+{penalty} pts)",
            expanded=True,
        ):
            st.markdown(
                f'<div class="evidence-quote-box">"{extracted}"</div>',
                unsafe_allow_html=True,
            )
            st.write(f"**Deception Analysis & Remediation:** {guidance}")


def main() -> None:
    """Primary application orchestrator."""
    configure_page_layout()
    pipeline = get_pipeline()
    report_generator = get_report_generator()

    raw_text, file_name = render_sidebar()

    st.title("Financial Instrument Regulatory Compliance Cockpit")
    st.markdown(
        "Automated statutory auditing engine evaluating high-yield agreements, syndication contracts, "
        "and promotional disclosures against SEC, FTC, FATF, and FCA enforcement doctrines."
    )

    contract_input = st.text_area(
        "Contractual Disclosures & Operative Provisions:",
        value=raw_text,
        height=180,
        placeholder="Upload document in sidebar or paste text content here...",
    )

    action_col1, action_col2 = st.columns([2, 1])
    with action_col1:
        run_audit = st.button(
            "Execute Regulatory Audit",
            type="primary",
            width="stretch",
        )
    with action_col2:
        export_placeholder = st.empty()

    if run_audit and contract_input.strip():
        start_time = time.perf_counter()
        with st.spinner("Executing statutory heuristic scan and vector decomposition..."):
            audit_result = pipeline.process_document(raw_text=contract_input, file_name=file_name)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        st.session_state["active_report"] = audit_result
        st.session_state["active_latency_ms"] = elapsed_ms

    if "active_report" in st.session_state:
        active_report: AuditAssessmentReport = st.session_state["active_report"]
        latency_ms: float = st.session_state.get("active_latency_ms", 0.0)

        # Generate court-admissible PDF bytes
        pdf_bytes = report_generator.generate_pdf_bytes(active_report)
        export_placeholder.download_button(
            label="Export Forensic PDF Dossier",
            data=pdf_bytes,
            file_name=f"FinGuard_Forensic_Dossier_{active_report.document_id[:8]}.pdf",
            mime="application/pdf",
            width="stretch",
            help="Generates an institutional audit dossier with SHA-256 cryptographic provenance.",
        )

        st.markdown("---")
        render_telemetry_kpis(active_report, latency_ms)

        # Decomposed Risk Vector & Executive Summary
        chart_col, summary_col = st.columns([1.1, 1.0], gap="medium")

        with chart_col:
            st.subheader("Orthogonal 4D Risk Exposure")
            st.plotly_chart(build_risk_radar_chart(active_report), use_container_width=True)

        with summary_col:
            st.subheader("Executive Auditor Summary")
            st.info(active_report.executive_summary)

            v = active_report.risk_vector
            st.markdown(
                f"""
                - **Yield Velocity Risk:** `{v.yield_risk}/100`
                - **Structural / MLM Risk:** `{v.structural_risk}/100`
                - **Liquidity Lockup Risk:** `{v.liquidity_risk}/100`
                - **Jurisdiction Evasion Risk:** `{v.legal_risk}/100`
                """
            )

        # Detailed Breakdown Tabs
        st.markdown("---")
        tab_findings, tab_directives, tab_payload = st.tabs(
            [
                "Itemized Infractions & Evidence",
                "Statutory Remediation Directives",
                "Audit Artifact Data",
            ]
        )

        with tab_findings:
            render_findings_tab(active_report)

        with tab_directives:
            st.subheader("Actionable Governance Directives")
            if not active_report.remediation_actions:
                st.write("No statutory remediation actions prescribed.")
            else:
                for idx, action in enumerate(active_report.remediation_actions, start=1):
                    st.markdown(f"**{idx}.** {action}")

        with tab_payload:
            st.subheader("Serialized Audit Report (JSON)")
            st.json(active_report.model_dump())


if __name__ == "__main__":
    main()
