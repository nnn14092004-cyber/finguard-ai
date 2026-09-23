"""Cognitive semantic auditor evaluating obfuscated financial contracts via LLM analysis."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from src.core.config import get_settings
from src.domain.enums import RegulatoryFramework, Severity
from src.domain.models import DocumentPayload, SemanticFinding

logger = logging.getLogger("finguard.semantic_auditor")

SYSTEM_AUDIT_PROMPT = """You are a Senior Regulatory Enforcement Attorney and Forensic Financial Auditor representing the U.S. Securities and Exchange Commission (SEC), Federal Trade Commission (FTC), and Financial Action Task Force (FATF).

Your mandate is to examine investment agreements, digital asset contracts, and commercial offerings to detect EUPHEMISTIC OBFUSCATION, REGULATORY EVASION, and DISGUISED FRAUDULENT MECHANICS.

Evaluate the text strictly against these four governing legal benchmarks:
1. U.S. SEC Howey Doctrine: Unregistered securities offerings disguising passive investor reliance behind algorithmic trading, liquidity pools, or centralized management syndicates.
2. FTC Koscot & Amway Doctrines: Pyramid schemes compensating participants for downline capital recruitment rather than legitimate retail sales, utilizing multi-tier bonuses or binary leg balancing.
3. FATF & FCA High-Yield Fraud Standards: Structurally impossible return velocity (e.g., daily/monthly fixed yields), absolute capital protection claims, or algorithmic buzzwords masking revenue voids.
4. Unfair Contract Terms & Jurisdiction Evasion: Unilateral terms modification rights, extortionate lockups (>12 months) with exit penalties (>30%), and offshore secrecy haven arbitration clauses.

You must respond ONLY with a valid JSON array of objects matching this exact schema:
[
  {
    "clause_topic": "Short descriptive violation category",
    "extracted_text": "Verbatim excerpt illustrating the deceptive clause",
    "deceptive_intent": "Forensic explanation of how this clause obfuscates regulatory non-compliance",
    "implicit_risk_level": "CRITICAL" | "HIGH" | "MEDIUM",
    "regulatory_relevance": "HOWEY_TEST" | "FTC_KOSCOT" | "FATF_HYIP" | "UNFAIR_TERMS" | "JURISDICTION_EVASION",
    "penalty_weight": 40 | 20 | 10,
    "remediation_guidance": "Actionable statutory counsel required to achieve legal compliance"
  }
]

If no deceptive or predatory clauses are found, return an empty JSON array: [].
Do not include markdown code block formatting or any text outside the JSON array.
"""

FALLBACK_LINGUISTIC_SPECS: list[dict[str, Any]] = [
    {
        "pattern_str": r"(?:autonomous\s+neural|algorithmic|ai-driven)\s+(?:arbitrage|syndicate|matrix)",
        "topic": "Algorithmic Yield Obfuscation",
        "intent": "Masks centralized pooled investment operations under artificial intelligence terminology, satisfying Howey Test passive reliance criteria.",
        "risk_level": "CRITICAL",
        "framework": RegulatoryFramework.HOWEY_TEST.value,
        "weight": 40,
        "remediation": "Disclose algorithmic investment strategies under licensed statutory investment management frameworks.",
    },
    {
        "pattern_str": r"(?:generational|downline|matrix)\s+(?:yield|redistribution|rewards)\s+proportional\s+to\s+network",
        "topic": "Disguised Pyramid Recruitment",
        "intent": "Obfuscates multi-level capital recruitment commissions behind network consensus and liquidity provision terminology.",
        "risk_level": "CRITICAL",
        "framework": RegulatoryFramework.FTC_KOSCOT.value,
        "weight": 40,
        "remediation": "Sever investment yield distributions completely from downline capital onboarding metrics.",
    },
    {
        "pattern_str": r"(?:zero\s+directional|downside\s+mitigation)\s+without\s+directional\s+market\s+dependency",
        "topic": "Disguised Capital Guarantee",
        "intent": "Implies risk-free market decoupling, contradicting the fundamental financial risk-return tradeoff mandate.",
        "risk_level": "HIGH",
        "framework": RegulatoryFramework.FATF_HYIP.value,
        "weight": 20,
        "remediation": "Publish clear statutory risk disclaimers regarding market volatility and potential principal impairment.",
    },
    {
        "pattern_str": r"protocol\s+governance\s+reserves\s+the\s+right\s+to\s+(?:recalibrate|alter|amend)",
        "topic": "Unilateral Recalibration Asymmetry",
        "intent": "Reserves unconstrained unilateral authority to modify contractual commitments without investor counterparty consent.",
        "risk_level": "HIGH",
        "framework": RegulatoryFramework.UNFAIR_TERMS.value,
        "weight": 20,
        "remediation": "Require bilateral electronic consent before enacting binding amendments to yield schedules.",
    },
]


class SemanticAuditor:
    """Forensic NLP semantic inspection engine detecting predatory financial structures."""

    def __init__(self) -> None:
        """Initializes cognitive semantic auditor with cached compiled regex automata."""
        self.settings = get_settings()
        self.api_key: str = (
            self.settings.GEMINI_API_KEY.get_secret_value()
            if hasattr(self.settings, "GEMINI_API_KEY")
            and hasattr(self.settings.GEMINI_API_KEY, "get_secret_value")
            else getattr(self.settings, "GEMINI_API_KEY", "")
        )
        self.model_name: str = getattr(self.settings, "LLM_MODEL_NAME", "gemini-1.5-flash")
        self.api_url: str = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

        # Pre-compile linguistic patterns once during instantiation for sub-second execution
        self._compiled_fallback_rules: list[tuple[re.Pattern[str], dict[str, Any]]] = [
            (re.compile(spec["pattern_str"], re.IGNORECASE), spec)
            for spec in FALLBACK_LINGUISTIC_SPECS
        ]

    def audit(self, payload: DocumentPayload) -> list[SemanticFinding]:
        """Audits contract payload for deceptive terms using LLM or robust fallback logic."""
        text = payload.normalized_text or payload.raw_text
        if not text or not text.strip():
            return []

        if self.api_key and self.api_key.strip():
            try:
                findings = self._execute_llm_inference(text)
                if findings:
                    return findings
            except Exception as exc:
                logger.warning(
                    "LLM semantic inference encountered failure; activating heuristic fallback. Error: %s",
                    str(exc),
                )

        return self._execute_fallback_analysis(text)

    def _execute_llm_inference(self, contract_text: str) -> list[SemanticFinding]:
        """Dispatches contract text to LLM endpoint and enforces structured output schema."""
        truncated_text = contract_text[:12000]
        request_body = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                f"{SYSTEM_AUDIT_PROMPT}\n\n"
                                f"CONTRACT TEXT TO AUDIT:\n{truncated_text}"
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}

        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                self.api_url,
                params=params,
                headers=headers,
                json=request_body,
            )

        if response.status_code != 200:
            logger.error(
                "Upstream LLM provider returned non-200 status code: %d - %s",
                response.status_code,
                response.text,
            )
            return []

        response_json = response.json()
        raw_output_text = (
            response_json.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        return self._parse_structured_json(raw_output_text)

    def _parse_structured_json(self, raw_json_str: str) -> list[SemanticFinding]:
        """Parses and validates raw LLM output into strongly typed SemanticFinding domain objects."""
        if not raw_json_str or not raw_json_str.strip():
            return []

        clean_str = re.sub(r"^```(?:json)?\s*", "", raw_json_str.strip(), flags=re.IGNORECASE)
        clean_str = re.sub(r"\s*```$", "", clean_str)

        try:
            items = json.loads(clean_str)
            if not isinstance(items, list):
                return []

            findings: list[SemanticFinding] = []
            for item in items:
                if not isinstance(item, dict):
                    continue

                risk_level = str(item.get("implicit_risk_level", "HIGH")).upper()
                severity = Severity.HIGH
                if risk_level == "CRITICAL":
                    severity = Severity.CRITICAL
                elif risk_level == "MEDIUM":
                    severity = Severity.MEDIUM

                finding = SemanticFinding(
                    clause_topic=str(item.get("clause_topic", "Deceptive Structure")),
                    category=str(item.get("clause_topic", "Deceptive Structure")),
                    extracted_text=str(item.get("extracted_text", "")),
                    matched_text=str(item.get("extracted_text", "")),
                    context_snippet=str(item.get("extracted_text", "")),
                    deceptive_intent=str(item.get("deceptive_intent", "")),
                    implicit_risk_level=risk_level,
                    regulatory_relevance=str(item.get("regulatory_relevance", "HOWEY_TEST")),
                    severity=severity,
                    penalty_weight=int(item.get("penalty_weight", 20)),
                    weight=int(item.get("penalty_weight", 20)),
                    remediation_guidance=str(item.get("remediation_guidance", "")),
                    remediation_advice=str(item.get("remediation_guidance", "")),
                )
                findings.append(finding)
            return findings
        except Exception as parse_exc:
            logger.warning("Failed to parse structured JSON from LLM: %s", str(parse_exc))
            return []

    def _execute_fallback_analysis(self, text: str) -> list[SemanticFinding]:
        """Executes forensic cognitive heuristic scanning via cached pre-compiled automata."""
        findings: list[SemanticFinding] = []
        for pattern, spec in self._compiled_fallback_rules:
            match = pattern.search(text)
            if match:
                severity = Severity.HIGH
                if spec["risk_level"] == "CRITICAL":
                    severity = Severity.CRITICAL
                elif spec["risk_level"] == "MEDIUM":
                    severity = Severity.MEDIUM

                finding = SemanticFinding(
                    clause_topic=spec["topic"],
                    category=spec["topic"],
                    extracted_text=match.group(0),
                    matched_text=match.group(0),
                    context_snippet=match.group(0),
                    deceptive_intent=spec["intent"],
                    implicit_risk_level=spec["risk_level"],
                    regulatory_relevance=spec["framework"],
                    severity=severity,
                    penalty_weight=spec["weight"],
                    weight=spec["weight"],
                    remediation_guidance=spec["remediation"],
                    remediation_advice=spec["remediation"],
                )
                findings.append(finding)
        return findings
