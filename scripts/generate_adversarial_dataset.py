"""Adversarial Synthetic Contract Dataset Fuzzer for FinGuard-AI.

Generates 100 enterprise-grade PDF contracts (80 adversarial scam traps + 20 negative controls)
with needle-in-a-haystack clause distribution, page breaks, and complex legal formatting.
Additionally compiles a flagship multi-page adversarial Master Private Placement Memorandum.
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
FLAGSHIP_MASTER_PATH = OUTPUT_DIR / "flagship_master_adversarial_ppm.pdf"

BOILERPLATE_LEGAL_PAGES = [
    """
    ARTICLE I: DEFINITIONS AND RECITALS. In this Master Commercial Agreement, unless the statutory
    context explicitly dictates otherwise, capitalized covenants shall maintain meanings defined
    under Schedule 1. References to statutory enactments include all successor amendments ratified
    by competent regulatory jurisdictions. Descriptive headings are inserted solely for navigational
    convenience and shall not alter the operative substantive construction of covenants herein.
    The subscriber acknowledges that participation involves significant economic risk and that no
    regulatory authority has confirmed the accuracy or determined the adequacy of this disclosure.
    """,
    """
    ARTICLE II: REPRESENTATIONS AND FIDUCIARY WARRANTIES. Each corporate signatory warrants that it
    is duly chartered, validly incorporated, and maintaining unencumbered legal status. Each Party
    possesses authoritative corporate power to execute binding covenants, satisfy operational mandates,
    and undertake bilateral responsibilities without violating preexisting third-party encumbrances.
    Signatories covenant that all operational disclosures represent true and accurate statements of fact.
    """,
    """
    ARTICLE III: STATUTORY CONFIDENTIALITY AND SEVERABILITY. Signatories covenant that proprietary
    commercial information exchanged during operational execution shall remain strictly confidential.
    Should any provision of this Instrument be adjudged unenforceable by a competent court of law,
    remaining bilateral covenants shall survive with full legal validity, enforceability, and binding force.
    All notices shall be delivered via certified electronic mail to designated administrative contacts.
    """,
    """
    ARTICLE IV: TAX MATTERS AND ERISA REGULATORY COMPLIANCE. Prospective investors subject to the
    Employee Retirement Income Security Act of 1974 (ERISA) should consult qualified fiduciary counsel
    prior to executing capital allocation requests. The syndicate makes no representation regarding
    tax exempt status under United States Internal Revenue Code Section 501(c)(3) or foreign equivalents.
    Each subscriber assumes sole responsibility for sovereign fiscal withholding liabilities.
    """,
]

ADVERSARIAL_TRAP_TEMPLATES = [
    # Group A: FTC Koscot / Multi-Tier Downline Capital Referral
    (
        "FTC_KOSCOT_PYRAMID",
        """
        ARTICLE V: PARTICIPANT CAPITAL EXPANSION AND NETWORK REWARD COMMISSION.
        Section 5.1. Participants earn multi-tier referral commission on level 5 downline investment volume.
        Section 5.2. Matching bonus across binary legs shall be allocated upon newly recruited capital deposits.
        Section 5.3. Participants must purchase an AI starter package to qualify for network earnings.
        """,
    ),
    # Group B: SEC Howey Test / Guaranteed Passive Returns
    (
        "SEC_HOWEY_HYIP",
        """
        ARTICLE VI: LIQUIDITY ALLOCATION MATRIX AND RETURN COMMITMENT.
        Section 6.1. Participants allocate digital liquidity to our autonomous neural arbitrage syndicate.
        Section 6.2. We guarantee a fixed 2.5% daily return with complete insulation from downside market volatility.
        Section 6.3. Operational management is handled entirely by our algorithmic trading team with completely passive investors.
        """,
    ),
    # Group C: Unfair Contract Terms & Extortionate Lockups + HYIP
    (
        "UNFAIR_TERMS_LOCK",
        """
        ARTICLE VII: PRINCIPAL REDEMPTION INTERVALS AND FORFEITURE COVENANTS.
        Section 7.1. A mandatory 18-month lock-up period applies to all deposited investor capital.
        Section 7.2. Early withdrawal penalty fees strip 40% of initial principal upon premature exit.
        Section 7.3. Protocol governance reserves the right to modify yield rates unilaterally without prior notice.
        Section 7.4. Participants receive guaranteed 2.0% daily return allocated from centralized liquidity reserves.
        """,
    ),
    # Group D: FATF Evasion & Jurisdiction Laundering
    (
        "FATF_AML_JURISDICTION",
        """
        ARTICLE VIII: DEPOSIT ROUTING AND DISPUTE RESOLUTION VENUE.
        Section 8.1. Investor shall deposit capital directly to anonymous personal crypto wallet without KYC.
        Section 8.2. Protocol provides 100% capital guarantee backed by proprietary offshore liquidity reserves.
        Section 8.3. Governed by the laws of Vanuatu, with disputes resolved exclusively via arbitration in Vanuatu tribunals.
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


def generate_pdf(file_path: Path, sections: list[str], document_title: str | None = None) -> None:
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
        fontSize=12,
        leading=16,
        spaceAfter=10,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=14,
        spaceAfter=8,
    )

    header_text = document_title or f"FORMAL COMMERCIAL DISCLOSURE - REF: {file_path.stem.upper()}"
    story = [
        Paragraph(header_text, title_style),
        Spacer(1, 10),
    ]

    for i, section in enumerate(sections):
        story.append(Paragraph(section.strip().replace("\n", "<br/>"), body_style))
        if i < len(sections) - 1:
            story.append(PageBreak())

    doc.build(story)


def generate_flagship_master_ppm(destination_path: Path) -> None:
    """Compiles an 8-page comprehensive adversarial PPM unifying all regulatory trap pillars."""
    master_sections = [
        # Page 1: Title & Corporate Recitals
        """
        CONFIDENTIAL PRIVATE PLACEMENT MEMORANDUM & INVESTMENT SYNDICATE AGREEMENT
        SERIES 2026-NEURAL ARBITRAGE LIQUIDITY VAULT
        
        This Private Placement Memorandum contains privileged commercial information regarding
        the Aura Neural Yield Protocol. Participation is strictly restricted to verified qualifying
        subscribers. Before executing capital committals, each prospective participant must conduct
        independent statutory due diligence regarding cross-border financial risk factors.
        """,
        # Page 2: Boilerplate Definitions & Fiduciary Covenants
        BOILERPLATE_LEGAL_PAGES[0],
        # Page 3: Pillar I & III - SEC Howey & FATF HYIP (Obfuscated hyphenation)
        """
        ARTICLE V: QUANTUM ALGORITHMIC YIELD POOLING (SEC HOWEY & FATF BENCHMARKS).
        Section 5.1. Capital Allocation: Subscribers commit sovereign liquidity into our centralized trading vault.
        Section 5.2. Passive Reliance: Operational trading is managed entirely by our algorithmic team with
        completely passive investors holding zero operational governance responsibilities.
        Section 5.3. Fixed Return Assurance: The system guarantees a fixed 2.5% daily return with absolute
        principal insulation against adverse macroeconomic volatility via our reserve architecture.
        """,
        # Page 4: Pillar II - FTC Koscot Pyramid & Multi-Tier Matrix
        """
        ARTICLE VI: GENERATIONAL RECRUITMENT BONUS & BINARY OVERRIDES (FTC KOSCOT STANDARDS).
        Section 6.1. Multi-Tier Compensation: Participants earn multi-tier referral\ncommission extending down to
        level 5 downline investment volume without requiring retail commercial product distribution.
        Section 6.2. Binary Volume Balancing: Residual matching bonus across binary legs shall be credited
        weekly upon newly recruited capital deposits.
        Section 6.3. Mandatory Node License: Active yield accrual remains strictly contingent upon the mandatory
        purchase of an initial AI starter package valued at five hundred United States dollars.
        """,
        # Page 5: Boilerplate Tax, ERISA, and Corporate Severability
        BOILERPLATE_LEGAL_PAGES[3],
        # Page 6: Pillar IV - Unfair Terms & Predatory Lockups
        """
        ARTICLE VII: LIQUIDITY CONSTRAINTS AND COVENANT MODIFICATIONS (UNFAIR TERMS BENCHMARKS).
        Section 7.1. Mandatory Capital Freeze: All deposited liquidity is subject to an irrevocable 18-\nmonth
        lock-up period to guarantee protocol liquidity preservation.
        Section 7.2. Liquidated Damages: Premature capital liquidation triggers an early\nwithdrawal penalty
        stripping 40% of initial principal upon premature exit.
        Section 7.3. Unilateral Discretion: Governance reserves the exclusive right to modify yield rates,
        disbursement schedules, and collateral requirements unilaterally without prior electronic notice.
        """,
        # Page 7: Pillar IV - FATF AML Circumvention & Secrecy Jurisdiction Laundering
        """
        ARTICLE VIII: ANONYMOUS SETTLEMENT AND DISPUTE RESOLUTION FORUM.
        Section 8.1. Settlement Channel: Subscribers shall deposit capital directly to anonymous personal crypto
        wallet addresses without identity verification or Travel Rule documentation.
        Section 8.2. Capital Guarantee: Protocol provides 100% capital guarantee backed by offshore liquidity reserves.
        Section 8.3. Forum Non Conveniens: This Instrument is governed exclusively under the laws of Vanuatu,
        with all bilateral disputes resolved exclusively via binding arbitration in Vanuatu tribunals.
        """,
        # Page 8: Execution Counterparts & Signatures
        """
        ARTICLE IX: COUNTERPART EXECUTION AND CLOSING MEMORANDUM.
        IN WITNESS WHEREOF, the authorized corporate officers and subscribing syndicate members have executed
        this Master Agreement as of the calendar date referenced below. Counterpart signatures transmitted
        electronically shall be deemed original, legally binding instruments across all competent jurisdictions.
        
        [EXECUTED BY SUBSCRIBER AND CENTRAL PROTOCOL FIDUCIARY ON SEPTEMBER 24, 2026]
        """,
    ]

    generate_pdf(
        destination_path,
        master_sections,
        document_title="AURA NEURAL PROTOCOL - MASTER SYNDICATE PPM (CONFIDENTIAL)",
    )


def main() -> None:
    """Generates the 100 benchmark PDF contracts, writes ground_truth.json, and compiles flagship master PPM."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ground_truth: dict[str, Any] = {}

    print("=== Generating 80 Adversarial Scam Trap Contracts (Needle-in-a-Haystack) ===")
    for idx in range(1, 81):
        filename = f"trap_scam_{idx:03d}.pdf"
        trap_type, trap_content = ADVERSARIAL_TRAP_TEMPLATES[
            (idx - 1) % len(ADVERSARIAL_TRAP_TEMPLATES)
        ]

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

    print("=== Compiling 8-Page Flagship Master Adversarial PPM ===")
    generate_flagship_master_ppm(FLAGSHIP_MASTER_PATH)
    print(f"SUCCESS: Compiled Flagship Master Specimen at: {FLAGSHIP_MASTER_PATH}")


if __name__ == "__main__":
    main()
