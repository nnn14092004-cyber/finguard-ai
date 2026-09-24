"""Court-admissible forensic audit report PDF generator for FinGuard-AI."""

from __future__ import annotations

import hashlib
import io
from datetime import UTC, datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch

try:
    from reportlab.platypus import (
        HRFlowable,
        KeepTogether,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
except ImportError:
    from reportlab.platypus import (
        KeepTogether,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.platypus.flowables import HRFlowable

from src.domain.enums import RegulatoryFramework, RiskTier, Severity
from src.domain.models import AuditAssessmentReport


def _escape_xml(text: str) -> str:
    """Escapes special XML/HTML entities for ReportLab Paragraph rendering."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


class ForensicReportGenerator:
    """Compiles strongly-typed compliance reports into court-admissible PDF dossiers."""

    def __init__(self) -> None:
        self.styles = getSampleStyleSheet()
        self._init_custom_typography()

    def _init_custom_typography(self) -> None:
        """Defines strict institutional typography hierarchy for legal dossiers."""
        self.title_style = ParagraphStyle(
            "DocTitle",
            parent=self.styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=6,
        )
        self.subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=self.styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#475569"),
            spaceAfter=14,
        )
        self.section_heading = ParagraphStyle(
            "SectionHeading",
            parent=self.styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True,
        )
        self.body_style = ParagraphStyle(
            "BodyDark",
            parent=self.styles["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )
        self.code_style = ParagraphStyle(
            "CodeMono",
            parent=self.styles["Code"],
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#0f172a"),
            fontName="Courier",
        )
        self.evidence_quote = ParagraphStyle(
            "EvidenceQuote",
            parent=self.styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#991b1b"),
            fontName="Helvetica-Oblique",
        )

    def _get_tier_badge_color(self, tier: RiskTier) -> tuple[colors.Color, colors.Color]:
        """Maps RiskTier enum to foreground and background color codes."""
        if tier == RiskTier.RED_FLAG:
            return colors.HexColor("#ef4444"), colors.HexColor("#fef2f2")
        if tier == RiskTier.ORANGE:
            return colors.HexColor("#f97316"), colors.HexColor("#fff7ed")
        if tier == RiskTier.YELLOW:
            return colors.HexColor("#eab308"), colors.HexColor("#fefce8")
        return colors.HexColor("#10b981"), colors.HexColor("#ecfdf5")

    def generate_pdf_bytes(self, report: AuditAssessmentReport) -> bytes:
        """Generates an in-memory PDF byte stream for instant HTTP downloads."""
        buffer = io.BytesIO()
        self._build_document(buffer, report)
        return buffer.getvalue()

    def generate_pdf_file(self, report: AuditAssessmentReport, output_path: str | Path) -> Path:
        """Writes legal audit dossier directly to disk destination."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(self.generate_pdf_bytes(report))
        return path

    def _build_document(self, output_stream: io.BytesIO, report: AuditAssessmentReport) -> None:
        """Compiles ReportLab story elements into formatted multi-page PDF."""
        doc = SimpleDocTemplate(
            output_stream,
            pagesize=letter,
            leftMargin=0.6 * inch,
            rightMargin=0.6 * inch,
            topMargin=0.6 * inch,
            bottomMargin=0.6 * inch,
        )
        story = []

        # 1. Header Banner & Document Identity
        story.append(Paragraph("FINGUARD-AI STATUTORY AUDIT DOSSIER", self.title_style))
        story.append(
            Paragraph(
                f"Formal Regulatory Examination Report | Document Ref: <b>{_escape_xml(report.file_name)}</b>",
                self.subtitle_style,
            )
        )
        story.append(
            HRFlowable(
                width="100%",
                thickness=1.5,
                color=colors.HexColor("#0ea5e9"),
                spaceAfter=10,
            )
        )

        # 2. Cryptographic Provenance & Telemetry Matrix
        timestamp_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        payload_source = report.raw_content or report.document_id
        sha256_stamp = hashlib.sha256(payload_source.encode("utf-8")).hexdigest()

        telemetry_data = [
            [
                Paragraph("<b>Document ID:</b>", self.body_style),
                Paragraph(report.document_id, self.code_style),
                Paragraph("<b>Audit Timestamp:</b>", self.body_style),
                Paragraph(timestamp_str, self.body_style),
            ],
            [
                Paragraph("<b>SHA-256 Provenance:</b>", self.body_style),
                Paragraph(sha256_stamp, self.code_style),
                Paragraph("<b>Scoring Profile:</b>", self.body_style),
                Paragraph("v1.0.0 (Global Regulatory Matrix)", self.body_style),
            ],
        ]
        telemetry_table = Table(
            telemetry_data, colWidths=[1.4 * inch, 2.5 * inch, 1.4 * inch, 2.0 * inch]
        )
        telemetry_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(telemetry_table)
        story.append(Spacer(1, 12))

        # 3. Executive Assessment & Risk Disposition Banner
        fg_color, bg_color = self._get_tier_badge_color(report.risk_tier)
        summary_box = [
            [
                Paragraph(
                    f"<font size=14 color='{fg_color.hexval()}'><b>STATUTORY TIER: {report.risk_tier.value}</b></font><br/>"
                    f"Aggregate Regulatory Suspicion Score: <b>{report.suspicion_score}/100</b>",
                    self.body_style,
                ),
                Paragraph(
                    f"<b>Infractions Detected:</b> {report.total_findings}<br/>"
                    f"<b>Heuristic Deterministic:</b> {len(report.findings)} | "
                    f"<b>Cognitive Semantic:</b> {len(report.semantic_findings)}",
                    self.body_style,
                ),
            ]
        ]
        summary_table = Table(summary_box, colWidths=[4.3 * inch, 3.0 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), bg_color),
                    ("BOX", (0, 0), (-1, -1), 1.5, fg_color),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 10))

        # 4. Orthogonal 4D Exposure Vector Matrix
        story.append(
            Paragraph("1. Orthogonal Four-Dimensional Exposure Vector", self.section_heading)
        )
        v = report.risk_vector
        vector_data = [
            [
                Paragraph("<b>Yield Velocity Risk:</b>", self.body_style),
                Paragraph(f"{v.yield_risk}/100", self.body_style),
                Paragraph("<b>Structural / MLM Risk:</b>", self.body_style),
                Paragraph(f"{v.structural_risk}/100", self.body_style),
            ],
            [
                Paragraph("<b>Liquidity Lockup Risk:</b>", self.body_style),
                Paragraph(f"{v.liquidity_risk}/100", self.body_style),
                Paragraph("<b>Jurisdiction Evasion Risk:</b>", self.body_style),
                Paragraph(f"{v.legal_risk}/100", self.body_style),
            ],
        ]
        vector_table = Table(
            vector_data, colWidths=[1.8 * inch, 1.8 * inch, 1.8 * inch, 1.9 * inch]
        )
        vector_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(vector_table)
        story.append(Spacer(1, 10))

        # 5. Executive Summary
        story.append(Paragraph("2. Auditor Executive Summary", self.section_heading))
        story.append(Paragraph(_escape_xml(report.executive_summary), self.body_style))
        story.append(Spacer(1, 12))

        # 6. Verbatim Predatory Infractions Table
        story.append(
            Paragraph(
                "3. Detailed Predatory Clause Extractions & Evidence",
                self.section_heading,
            )
        )
        if not report.findings and not report.semantic_findings:
            story.append(
                Paragraph(
                    "<i>Zero statutory infractions detected. Agreement conforms to commercial baseline standards.</i>",
                    self.body_style,
                )
            )
        else:
            findings_data = [
                [
                    Paragraph("<b>Rule & Framework</b>", self.body_style),
                    Paragraph("<b>Severity</b>", self.body_style),
                    Paragraph("<b>Weight</b>", self.body_style),
                    Paragraph("<b>Verbatim Predatory Quote & Remediation</b>", self.body_style),
                ]
            ]
            for f in report.findings:
                framework_str = (
                    f.regulatory_framework.value
                    if isinstance(f.regulatory_framework, RegulatoryFramework)
                    else f.regulatory_framework
                )
                severity_str = f.severity.value if isinstance(f.severity, Severity) else f.severity
                clean_quote = _escape_xml(f.matched_text.replace("\n", " ").strip())
                if len(clean_quote) > 160:
                    clean_quote = clean_quote[:157] + "..."

                clean_remediation = _escape_xml(f.remediation_advice)

                rule_cell = f"<b>{_escape_xml(f.rule_id)}</b><br/><font size=7 color='#64748b'>{_escape_xml(framework_str)}</font>"
                severity_cell = f"<font color='#dc2626'><b>{_escape_xml(severity_str)}</b></font>"
                quote_cell = (
                    f'Quote: <i>"{clean_quote}"</i><br/>'
                    f"<font color='#047857'>Remediation: {clean_remediation}</font>"
                )
                findings_data.append(
                    [
                        Paragraph(rule_cell, self.body_style),
                        Paragraph(severity_cell, self.body_style),
                        Paragraph(f"+{f.weight}", self.body_style),
                        Paragraph(quote_cell, self.evidence_quote),
                    ]
                )

            findings_table = Table(
                findings_data,
                colWidths=[1.8 * inch, 1.0 * inch, 0.6 * inch, 3.9 * inch],
            )
            findings_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.append(findings_table)

        story.append(Spacer(1, 14))

        # 7. Actionable Remediation Directives
        story.append(
            KeepTogether(
                [
                    Paragraph(
                        "4. Statutory Remediation & Governance Directives",
                        self.section_heading,
                    ),
                    *[
                        Paragraph(f"• {_escape_xml(action)}", self.body_style)
                        for action in report.remediation_actions
                    ],
                    Spacer(1, 14),
                    HRFlowable(
                        width="100%",
                        thickness=0.5,
                        color=colors.HexColor("#cbd5e1"),
                        spaceAfter=6,
                    ),
                    Paragraph(
                        "DISCLAIMER: This forensic audit dossier is mechanically generated via statutory automata "
                        "and cryptographic verification routines. It reflects codified compliance criteria under "
                        "U.S. SEC, FTC, FATF, and FCA benchmarks. It does not replace sovereign prosecutorial action.",
                        self.subtitle_style,
                    ),
                ]
            )
        )

        doc.build(story)
