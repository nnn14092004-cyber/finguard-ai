"""Streamlit Executive Dashboard GUI for FinGuard-AI.

Provides an enterprise-grade compliance interface supporting:
1. Multi-format contract document uploads (.txt, .md, .pdf)
2. Interactive text pasting and pre-loaded fraudulent presets
3. Multi-dimensional risk scoring with 4D Plotly Radar charts
4. Verbatim regulatory finding drill-downs and actionable legal remediation
"""

from __future__ import annotations

import importlib.util
import io
from typing import Any, Tuple
import plotly.graph_objects as go
import streamlit as st

from src.domain.enums import RiskTier
from src.pipeline import FinGuardPipeline

# Page Configuration
st.set_page_config(
    page_title="FinGuard-AI | Enterprise Risk Audit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Enterprise CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #A0AEC0;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 16px;
        border-radius: 4px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_pipeline() -> FinGuardPipeline:
    """Initializes and caches the FinGuard master audit pipeline."""
    return FinGuardPipeline()


pipeline = get_pipeline()


def extract_content_from_upload(uploaded_file: Any) -> Tuple[str, str]:
    """Defensively extracts plain text content and filename from an uploaded file."""
    file_name = getattr(uploaded_file, "name", "uploaded_document.txt")
    raw_bytes = uploaded_file.read()

    # Dynamic inspection avoids static type-checker missing import warnings
    if file_name.lower().endswith(".pdf"):
        if importlib.util.find_spec("pypdf") is not None:
            try:
                import pypdf

                pdf_reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
                extracted_pages = [page.extract_text() or "" for page in pdf_reader.pages]
                return "\n".join(extracted_pages), file_name
            except Exception as exc:
                st.error(f"Error reading PDF stream: {exc}")
        else:
            st.warning(
                "Optional package `pypdf` is not installed. PDF text extraction skipped. "
                "Install via: `pip install pypdf` to enable PDF support."
            )

    # Default fallback: UTF-8 with Latin-1 safety net
    try:
        return raw_bytes.decode("utf-8"), file_name
    except UnicodeDecodeError:
        return raw_bytes.decode("latin-1", errors="replace"), file_name


# Synthetic Malicious Contract Preset
DEFAULT_PREDATORY_SAMPLE = """AURA NEURAL PROTOCOL:
Participants deposit capital into our autonomous liquidity allocation matrix.
The protocol targets an algorithmic distribution benchmark yielding 150 basis points daily,
backed by autonomous arbitrage with complete insulation from downside principal volatility.
No trading expertise is required by passive participants.
Earn returns through our multi-tier referral commission structure with downline investment
volume bonuses and a binary bonus on newly recruited capital.
Participants must purchase an AI license package to qualify.
Mandatory lock-up period of 24 months applies with an early withdrawal penalty of 40%.
Withdrawals are conditioned upon active referrals.
Governed by the laws of Seychelles, arbitration in Vanuatu."""

# Sidebar: Regulatory Benchmarks
with st.sidebar:
    st.title("🛡️ FinGuard-AI")
    st.markdown("### **Regulatory Standards**")
    st.markdown(
        """
        - **FATF & FCA**: High-Yield Investment Fraud (HYIP) & Yield Guarantees
        - **SEC Howey Doctrine**: Investment Contracts & Passive Pooling
        - **FTC Koscot Doctrine**: Pyramid Structures & Binary Recruitment
        - **Unfair Contract Terms**: Liquidity Entrapment & Offshore Havens
        """
    )
    st.divider()
    st.markdown("### **Engine Diagnostics**")
    st.success("✔ Heuristic Regex Engine: Active")
    st.success("✔ Semantic Contextual Auditor: Active")
    st.success("✔ Multi-Dimensional Risk Vector: Active")

# Main Header
st.markdown('<div class="main-header">🛡️ FinGuard-AI: Financial Contract Compliance Auditor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Automated Multilateral Financial Fraud Detection & Multi-Dimensional Risk Scoring</div>',
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([1.1, 1], gap="large")

with left_col:
    st.subheader("Contract Document Ingestion")

    # Ingestion Tabs: File Upload vs Text Input
    tab_upload, tab_text = st.tabs(["📂 Upload Document File", "✍️ Direct Text Input"])

    contract_text = ""
    active_doc_name = "contract_draft.txt"
    uploaded_doc = None

    with tab_upload:
        uploaded_doc = st.file_uploader(
            "Upload Investment Agreement, Prospectus, or Whitepaper:",
            type=["txt", "md", "pdf"],
            help="Supports plaintext (.txt), markdown (.md), and standard PDF agreements.",
            key="contract_uploader",
        )
        if uploaded_doc is not None:
            contract_text, active_doc_name = extract_content_from_upload(uploaded_doc)
            st.success(f"Loaded: `{active_doc_name}` ({len(contract_text):,} characters)")
            with st.expander("Preview Extracted Document Content"):
                st.text_area("File Content", value=contract_text, height=200, disabled=True)

    with tab_text:
        direct_name = st.text_input("Document Name", value="aura_neural_protocol.txt")
        pasted_text = st.text_area(
            "Paste Contract Clauses or Promotional Draft:",
            value=DEFAULT_PREDATORY_SAMPLE,
            height=280,
            key="direct_pasted_text",
        )
        if uploaded_doc is None:
            contract_text = pasted_text
            active_doc_name = direct_name

    execute_audit = st.button("🚀 Run Compliance Audit", type="primary", use_container_width=True)

# Audit Execution and Visualization
if execute_audit:
    if not contract_text or not contract_text.strip():
        st.error("Please upload a document file or provide contract text before running the audit.")
    else:
        with st.spinner("Executing normalization, deterministic heuristic scan, and semantic evaluation..."):
            report = pipeline.process_document(raw_text=contract_text, file_name=active_doc_name)

        with right_col:
            st.subheader("Executive Compliance Verdict")

            tier_colors = {
                RiskTier.RED_FLAG: "#FF4B4B",
                RiskTier.ORANGE: "#FFA500",
                RiskTier.YELLOW: "#F1C40F",
                RiskTier.GREEN: "#2ECC71",
            }
            theme_color = tier_colors.get(report.risk_tier, "#3498DB")

            m1, m2, m3 = st.columns(3)
            m1.metric("Suspicion Score", f"{report.suspicion_score}/100")
            m2.metric("Regulatory Tier", report.risk_tier.value)
            m3.metric("Total Findings", report.total_findings)

            # 4-Dimensional Risk Vector Radar Chart
            radar_categories = ["Yield Risk", "Structural Risk", "Liquidity Risk", "Legal Risk"]
            radar_values = [
                report.risk_vector.yield_risk,
                report.risk_vector.structural_risk,
                report.risk_vector.liquidity_risk,
                report.risk_vector.legal_risk,
            ]
            radar_values_closed = radar_values + [radar_values[0]]
            radar_categories_closed = radar_categories + [radar_categories[0]]

            fig = go.Figure(
                data=[
                    go.Scatterpolar(
                        r=radar_values_closed,
                        theta=radar_categories_closed,
                        fill="toself",
                        fillcolor=f"rgba({int(theme_color[1:3], 16)}, {int(theme_color[3:5], 16)}, {int(theme_color[5:7], 16)}, 0.35)",
                        line=dict(color=theme_color, width=3),
                        name="Assessed Risk Profile",
                    )
                ]
            )
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], color="#888888"),
                    angularaxis=dict(color="#FFFFFF", tickfont=dict(size=13, color="#FFFFFF")),
                    bgcolor="rgba(0,0,0,0)",
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=45, r=45, t=25, b=25),
                height=290,
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Detailed Inspection Tabs
        tab_findings, tab_remediation, tab_summary = st.tabs(
            ["📑 Verbatim Findings", "🛠️ Actionable Remediation", "📋 Executive Summary"]
        )

        with tab_findings:
            if report.findings:
                st.markdown(f"**Identified {len(report.findings)} Codified Violations:**")
                for idx, finding in enumerate(report.findings, start=1):
                    with st.expander(
                        f"#{idx} [{finding.severity.value}] {finding.rule_name} ({finding.rule_id}) — Penalty: +{finding.weight}"
                    ):
                        st.markdown(f"**Matched Contractual Clause:** `{finding.matched_text}`")
                        st.markdown(f"**Classification Category:** `{finding.category}`")
                        st.markdown(f"**Governing Regulatory Doctrine:** `{finding.regulatory_framework.value}`")
                        st.info(f"**Statutory Remediation Guidance:** {finding.remediation_advice}")
            else:
                st.success("Zero deterministic heuristic violations detected in this document.")

        with tab_remediation:
            st.markdown("### Statutory Remediation & Action Plan")
            for action in report.remediation_actions:
                st.warning(f"• {action}")

        with tab_summary:
            st.markdown("### Executive Compliance Narrative")
            st.info(report.executive_summary)