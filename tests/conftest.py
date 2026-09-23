"""Pytest fixtures providing standardized synthetic contracts for FinGuard tests."""

from __future__ import annotations

import uuid
from collections.abc import Callable

import pytest

from src.domain.models import DocumentPayload
from src.ingestion.normalizer import TextNormalizer


@pytest.fixture
def predatory_hyip_contract() -> str:
    """Returns a synthetic contract exhibiting Tier 1, 2, and 3 predatory clauses."""
    return """
    SYNAPSE QUANTUM VAULT - PARTICIPATION TERMS
    
    1. Capital Allocation & Yield:
    Investors allocate funds into our passive yield generation syndicate.
    The protocol yields a guaranteed 2.0% daily return, compounding continuously.
    We assert a 100% capital guarantee via algorithmic neural reserves.
    
    2. Affiliate Incentives:
    Members receive generous downline investment volume commissions across 5 generations,
    plus a binary bonus for active network leg balancing.
    
    3. Lockup & Liquidity Restrictions:
    All assets remain subject to a mandatory lock-up period of 18 months.
    Early withdrawal penalty fees strip 40% of the initial deposit balance.
    
    4. Alterations & Jurisdiction:
    The issuer reserves the right to modify these terms and withdrawal rules at any time 
    without prior notice at its sole discretion.
    This agreement is governed by the laws of Vanuatu.
    """


@pytest.fixture
def legitimate_saas_contract() -> str:
    """Returns an authentic standard commercial SaaS agreement without predatory terms."""
    return """
    ENTERPRISE CLOUD SERVICE LEVEL AGREEMENT (SLA)
    
    1. Scope of Services:
    Vendor provides scalable database hosting and distributed API gateway services.
    Customer pays a monthly recurring subscription fee based on compute resource consumption.
    
    2. Availability & Performance:
    Vendor targets a 99.9% uptime availability metric across all operational regions.
    Service credits are granted for verified unscheduled downtime exceeding permitted limits.
    
    3. Warranties & Disclaimers:
    Services are provided on an as-is basis without warranties of uninterrupted transmission.
    Neither party guarantees financial performance, profits, or third-party sales conversion rates.
    
    4. Term & Termination:
    This agreement may be terminated by either party upon 30 days written electronic notice.
    Unused prepaid amounts for unrendered services will be refunded pro-rata without penalty.
    
    5. Governing Law:
    This instrument is governed by the commercial laws of the State of Delaware, United States.
    """


@pytest.fixture
def obfuscated_scam_contract() -> str:
    """Returns a fraudulent contract utilizing deliberate character spacing to evade detection."""
    return """
    VIP ELITE WEALTH SYSTEM
    
    Investors receive a  g u a r a n t e e d  1 . 5 %  d a i l y  return on all deposits.
    Enjoy a 1 0 0 % capital protection safeguard powered by  q u a n t u m   a i  arbitrage.
    Earn commissions through our  m u l t i - t i e r  referral structure.
    Mandatory capital freeze applies for 2 4 months with early withdrawal fee of 5 0 %.
    Governed by the laws of  C a y m a n   I s l a n d s.
    """


@pytest.fixture
def blank_contract() -> str:
    """Returns a boundary test fixture containing only whitespace."""
    return "   \n\t  \r\n   "


@pytest.fixture
def create_payload() -> Callable[[str, str], DocumentPayload]:
    """Factory fixture generating valid DocumentPayload instances."""

    def _factory(raw_text: str, file_name: str = "test_document.txt") -> DocumentPayload:
        normalized = TextNormalizer.normalize(raw_text)
        return DocumentPayload(
            document_id=str(uuid.uuid4()),
            file_name=file_name,
            raw_content=raw_text,
            normalized_content=normalized,
            character_count=len(normalized),
        )

    return _factory
