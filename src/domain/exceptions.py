"""Enterprise Domain Exception Hierarchy for FinGuard-AI.

Decouples low-level runtime errors from regulatory and compliance domain failures.
Follows PEP 3151 standard design principles.
"""

from __future__ import annotations

from typing import Any


class FinGuardDomainException(Exception):
    """Base domain exception for all FinGuard compliance pipeline errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}

    def to_dict(self) -> dict[str, Any]:
        """Serializes domain exception for API and telemetry sinks."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
        }


class IngestionNormalizationError(FinGuardDomainException):
    """Raised when an inbound contract payload cannot be decoded or normalized."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            error_code="ERR_INGESTION_NORMALIZATION_FAILED",
            context=context,
        )


class RegulatoryRuleCompilationError(FinGuardDomainException):
    """Raised when an internal regulatory regex expression fails compilation."""

    def __init__(self, rule_id: str, pattern: str) -> None:
        super().__init__(
            message=f"Statutory rule '{rule_id}' failed pattern compilation: {pattern}",
            error_code="ERR_RULE_COMPILATION_FAILED",
            context={"rule_id": rule_id, "pattern": pattern},
        )


class UnregisteredSecuritiesViolationError(FinGuardDomainException):
    """Raised when a contract satisfies all prongs of the 1946 SEC Howey Test."""

    def __init__(self, context: dict[str, Any] | None = None) -> None:
        super().__init__(
            message="Contract manifests passive pooling syndication violating SEC Howey registration mandates.",
            error_code="ERR_SEC_HOWEY_UNREGISTERED_SECURITY",
            context=context,
        )


class UnrealisticYieldGuaranteeError(FinGuardDomainException):
    """Raised when contract promises mathematically untenable fiat-decoupled returns."""

    def __init__(self, claimed_yield: str, threshold: str) -> None:
        super().__init__(
            message=f"Promised yield '{claimed_yield}' breaches FATF/FCA realistic threshold '{threshold}'.",
            error_code="ERR_FATF_HYIP_DECOUPLING",
            context={"claimed_yield": claimed_yield, "threshold": threshold},
        )
