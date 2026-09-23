"""FastAPI REST gateway for FinGuard compliance auditing services."""

from __future__ import annotations

import logging
from typing import Any, Dict
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from src.domain.models import AuditAssessmentReport, ContractAuditRequest
from src.pipeline import FinGuardPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("finguard.api")

app = FastAPI(
    title="FinGuard Compliance Engine API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline_instance = FinGuardPipeline()


@app.get("/", tags=["Discovery"])
def root() -> Dict[str, Any]:
    """Returns service discovery metadata, navigation endpoints, and documentation links.

    Returns:
        Dictionary containing service identity, operational status, and endpoint paths.
    """
    return {
        "service": "FinGuard-AI Regulatory Gateway",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "audit_text": "/api/v1/audit/text",
            "audit_file": "/api/v1/audit/file",
            "docs": "/docs",
        },
    }


@app.get("/health", tags=["Telemetry"])
def health_check() -> Dict[str, str]:
    """Returns operational health telemetry status.

    Returns:
        Dictionary reporting service status, version, and identity.
    """
    return {
        "status": "healthy",
        "service": "FinGuard-AI Regulatory Gateway",
        "version": "1.0.0",
    }


@app.post(
    "/api/v1/audit/text",
    response_model=AuditAssessmentReport,
    status_code=status.HTTP_200_OK,
    tags=["Audit"],
)
def audit_text(request: ContractAuditRequest) -> AuditAssessmentReport:
    """Analyzes raw contract text and returns a comprehensive regulatory audit report.

    Args:
        request: Inbound audit payload containing contract text.

    Returns:
        AuditAssessmentReport containing findings, risk vector, and suspicion score.

    Raises:
        HTTPException: If payload content is blank or contains only whitespace.
    """
    if not request.content or not request.content.strip():
        logger.warning("audit_text_rejected: empty request content")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Contract content must contain substantive non-whitespace text.",
        )

    file_name = request.document_title or "contract_draft.txt"
    logger.info("audit_text_started: document=%s length=%d", file_name, len(request.content))
    return pipeline_instance.process_document(raw_text=request.content, file_name=file_name)


@app.post(
    "/api/v1/audit/file",
    response_model=AuditAssessmentReport,
    status_code=status.HTTP_200_OK,
    tags=["Audit"],
)
def audit_file(file: UploadFile = File(...)) -> AuditAssessmentReport:
    """Analyzes an uploaded plain text contract file.

    Args:
        file: Multi-part form file upload stream.

    Returns:
        AuditAssessmentReport containing compliance assessment findings.

    Raises:
        HTTPException: If file is missing a filename or contains an empty payload.
    """
    if not file.filename:
        logger.warning("audit_file_rejected: missing filename")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Uploaded file must possess a valid filename.",
        )

    raw_bytes = file.file.read()
    if not raw_bytes or not raw_bytes.strip():
        logger.warning("audit_file_rejected: empty payload for %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Uploaded file content cannot be empty.",
        )

    content = raw_bytes.decode("utf-8", errors="replace")
    logger.info("audit_file_started: filename=%s size=%d", file.filename, len(raw_bytes))
    return pipeline_instance.process_document(raw_text=content, file_name=file.filename)