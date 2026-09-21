"""FastAPI Gateway Application for FinGuard-AI.

Exposes RESTful endpoints for contract text and document file compliance auditing,
health checks, root service discovery, and multi-dimensional financial risk scoring
against international regulatory standards (FATF, SEC Howey, FTC Koscot, Unfair Terms).
"""

from __future__ import annotations

from typing import Any, Dict
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from src.domain.models import AuditAssessmentReport, ContractAuditRequest
from src.pipeline import FinGuardPipeline

app = FastAPI(
    title="FinGuard-AI Compliance & Regulatory Audit Gateway",
    description="Automated multi-dimensional financial contract risk scoring and regulatory auditing engine.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline_instance = FinGuardPipeline()


@app.get("/", status_code=status.HTTP_200_OK, tags=["System"])
async def root() -> Dict[str, Any]:
    """Root service discovery endpoint exposing operational metadata and documentation links."""
    return {
        "service": "FinGuard-AI Compliance & Regulatory Audit Gateway",
        "version": "1.0.0",
        "status": "operational",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "endpoints": {
            "health_check": "/health",
            "audit_text": "/api/v1/audit/text",
            "audit_file": "/api/v1/audit/file",
        },
    }


@app.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify gateway and sub-engine operational readiness."""
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
async def audit_text(request: ContractAuditRequest) -> AuditAssessmentReport:
    """Audits raw contract or promotional text payload for regulatory violations."""
    raw_content = request.content.strip()
    if not raw_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Contract content must not be blank or purely whitespace.",
        )
    return pipeline_instance.process_document(
        raw_content,
        file_name=request.document_title or "raw_contract_text.txt",
    )


@app.post(
    "/api/v1/audit/file",
    response_model=AuditAssessmentReport,
    status_code=status.HTTP_200_OK,
    tags=["Audit"],
)
async def audit_file(file: UploadFile = File(...)) -> AuditAssessmentReport:
    """Accepts uploaded text or markdown files and executes end-to-end audit pipeline."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file must have a valid filename.",
        )

    file_bytes = await file.read()
    if not file_bytes or not file_bytes.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file content is empty.",
        )

    try:
        decoded_text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        decoded_text = file_bytes.decode("latin-1", errors="replace")

    return pipeline_instance.process_document(
        decoded_text,
        file_name=file.filename,
    )


# Explicit function aliases for backward compatibility and test invocation
audit_contract_text = audit_text
audit_contract_file = audit_file