"""Adversarial Synthetic Contract Dataset Fuzzer for FinGuard-AI.

Generates 100 enterprise-grade PDF contracts (80 adversarial scam traps + 20 negative controls)
with needle-in-a-haystack clause distribution, page breaks, and complex legal formatting.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

OUTPUT_DIR = Path("data/benchmark")
GROUND_TRUTH_PATH = OUTPUT_DIR / "ground_truth.json"

BOILERPLATE_LEGAL_PAGES = [
    """
    ARTICLE I: DEFINITIONS AND RECITALS. In this Master Commercial Agreement, unless the statutory
    context explicitly dictates otherwise, capitalized covenants shall maintain meanings defined
    under Schedule 1. References to statutory enactments include all successor amendments ratified
    by competent regulatory jurisdictions. Descriptive headings are inserted solely for navigational
    convenience and shall not alter the operative substantive construction of covenants herein.
    """,
    """
    ARTICLE II: REPRESENTATIONS AND FIDUCIARY WARRANTIES. Each corporate signatory warrants that it
    is duly chartered, validly incorporated, and maintaining unencumbered legal status. Each Party
    possesses authoritative corporate power to execute binding covenants, satisfy operational mandates,
    and undertake bilateral responsibilities without violating preexisting third-party encumbrances.
    """,
    """
    ARTICLE III: STATUTORY CONFIDENTIALITY AND SEVERABILITY. Signatories covenant that proprietary
    commercial information exchanged during operational execution shall remain strictly confidential.
    Should any provision of this Instrument be adjudged unenforceable by a competent court of law,
    remaining bilateral covenants shall survive with full legal validity, enforceability, and binding force.
    """,
]

ADVERSARIAL_TRAP_TEMPLATES = [
    # Group A: FTC Koscot / Multi-Tier Downline Capital Referral (Score: 100 >= 75)
    (
        "FTC_KOSCOT_PYRAMID",
        """
        ARTICLE IV: PARTICIPANT CAPITAL EXPANSION AND NETWORK REWARD COMMISSION.
        Section 4.1. Participants earn multi-tier referral commission on level 5 downline investment volume.
        Section 4.2. Matching bonus across binary legs shall be allocated upon newly recruited capital deposits.
        Section 4.3. Participants must purchase an AI starter package to qualify for network earnings.
        """,
    ),
    # Group B: SEC Howey Test / Guaranteed Passive Returns (Score: 100 >= 75)
    (
        "SEC_HOWEY_HYIP",
        """
        ARTICLE V: LIQUIDITY ALLOCATION MATRIX AND RETURN COMMITMENT.
        Section 5.1. Participants allocate digital liquidity to our autonomous neural arbitrage syndicate.
        Section 5.2. We guarantee a fixed 2.5% daily return with complete insulation from downside market volatility.
        Section 5.3. Operational management is handled entirely by our algorithmic trading team with completely passive investors.
        """,
    ),
    # Group C: Unfair Contract Terms & Extortionate Lockups + HYIP (Score: 100 >= 75)
    (
        "UNFAIR_TERMS_LOCK",
        """
        ARTICLE VI: PRINCIPAL REDEMPTION INTERVALS AND FORFEITURE COVENANTS.
        Section 6.1. A mandatory 18-month lock-up period applies to all deposited investor capital.
        Section 6.2. Early withdrawal penalty fees strip 40% of initial principal upon premature exit.
        Section 6.3. Protocol governance reserves the right to modify yield rates unilaterally without prior notice.
        Section 6.4. Participants receive guaranteed 2.0% daily return allocated from centralized liquidity reserves.
        """,
    ),
    # Group D: FATF Evasion & Jurisdiction Laundering (Score: 100 >= 75)
    (
        "FATF_AML_JURISDICTION",
        """
        ARTICLE VII: DEPOSIT ROUTING AND DISPUTE RESOLUTION VENUE.
        Section 7.1. Investor shall deposit capital directly to anonymous personal crypto wallet without KYC.
        Section 7.2. Protocol provides 100% capital guarantee backed by proprietary offshore liquidity reserves.
        Section 7.3. Governed by the laws of Vanuatu, with disputes resolved exclusively via arbitration in Vanuatu tribunals.
        """,
    ),
]

CLEAN_LEGAL_TEMPLATES = [
    (
        "SHAREHOLDERS_AGREEMENT",
        """
        SERIES A PREFERRED SHAREHOLDERS AGREEMENT:
        1. Founder Equity Lock-up: Founders agree to a standard founder share lock-up following
           the execution of this Agreement, subject to a four-year linear vesting schedule with a one-year cliff.
        2. Transfer Restrictions: No Shareholder shall transfer, pledge, or encumber common stock without
           prior written consent of the Board of Directors representing a qualified corporate majority.
        3. Governing Law: Governed in accordance with the laws of the State of Delaware, United States.
        """,
    ),
    (
        "CORPORATE_BOND_INDENTURE",
        """
        SENIOR UNSECURED CORPORATE BOND INDENTURE:
        1. Coupon Payment: Issuer covenants to pay semi-annual interest at a fixed coupon rate of 6.5% per annum.
        2. Principal Redemption: 100% of the outstanding principal amount shall be redeemed at maturity in 2030.
        3. Fiduciary Covenants: Issuer shall maintain a Consolidated Leverage Ratio not exceeding 3.50 to 1.00.
        4. Jurisdiction: Competent state and federal commercial courts in the City of London, England.
        """,
    ),
    (
        "ENTERPRISE_SAAS_AGREEMENT",
        """
        MASTER ENTERPRISE SOFTWARE SUBSCRIPTION AGREEMENT:
        1. Service Availability: Provider shall maintain monthly system availability of at least 99.9%.
        2. Tiered Platform License: Customer is licensed for up to 500 concurrent administrative seats.
        3. Bilateral Termination: Either party may terminate upon 30 days written notice for uncured material breach.
        4. Liability Cap: Total aggregate liability shall not exceed fees paid in the preceding twelve months.
        """,
    ),
    (
        "COMMERCIAL_OFFICE_LEASE",
        """
        COMMERCIAL REAL ESTATE LEASE AGREEMENT:
        1. Base Rent: Tenant covenants to pay monthly base rent on the first calendar day of each month.
        2. Security Deposit: Landlord holds an amount equal to two months' base rent as a security reserve.
        3. Permitted Use: Premises shall be utilized exclusively for general executive and software engineering offices.
        4. Municipal Compliance: Tenant shall strictly adhere to all applicable municipal fire and commercial zoning codes.
        """,
    ),
]


def generate_pdf(file_path: Path, sections: list[str]) -> None:
    """Compiles text sections into a multi-page, formatted legal PDF document."""
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=13,
        leading=17,
        spaceAfter=10,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=14,
        spaceAfter=8,
    )

    story = [
        Paragraph(f"FORMAL COMMERCIAL DISCLOSURE - REF: {file_path.stem.upper()}", title_style),
        Spacer(1, 10),
    ]

    for i, section in enumerate(sections):
        story.append(Paragraph(section.strip().replace("\n", "<br/>"), body_style))
        if i < len(sections) - 1:
            story.append(PageBreak())

    doc.build(story)


def main() -> None:
    """Generates the 100 benchmark PDF contracts and writes ground_truth.json."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ground_truth: dict[str, Any] = {}

    print("=== Generating 80 Adversarial Scam Trap Contracts (Needle-in-a-Haystack) ===")
    for idx in range(1, 81):
        filename = f"trap_scam_{idx:03d}.pdf"
        trap_type, trap_content = ADVERSARIAL_TRAP_TEMPLATES[
            (idx - 1) % len(ADVERSARIAL_TRAP_TEMPLATES)
        ]

        # Simulate needle-in-a-haystack & cross-line hyphenation stress
        stressed_trap = trap_content.replace("18-month", "18-\nmonth").replace(
            "early withdrawal", "early\nwithdrawal"
        )

        pages = [
            BOILERPLATE_LEGAL_PAGES[0],
            BOILERPLATE_LEGAL_PAGES[1],
            stressed_trap,
            BOILERPLATE_LEGAL_PAGES[2],
        ]

        generate_pdf(OUTPUT_DIR / filename, pages)
        ground_truth[filename] = {
            "expected_tier": "RED",
            "is_adversarial": True,
            "category": trap_type,
            "expected_min_score": 75,
        }

    print("=== Generating 20 Negative Control Clean Commercial Contracts ===")
    for idx in range(1, 21):
        filename = f"clean_control_{idx:03d}.pdf"
        clean_type, clean_content = CLEAN_LEGAL_TEMPLATES[(idx - 1) % len(CLEAN_LEGAL_TEMPLATES)]

        pages = [
            BOILERPLATE_LEGAL_PAGES[0],
            clean_content,
            BOILERPLATE_LEGAL_PAGES[1],
        ]

        generate_pdf(OUTPUT_DIR / filename, pages)
        ground_truth[filename] = {
            "expected_tier": "GREEN",
            "is_adversarial": False,
            "category": clean_type,
            "expected_max_score": 24,
        }

    with open(GROUND_TRUTH_PATH, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2)

    print(
        f"SUCCESS: Generated 100 contracts in {OUTPUT_DIR}/ with ground truth in {GROUND_TRUTH_PATH}"
    )


if __name__ == "__main__":
    main()
