"""FastAPI surface for the pipeline.

Mirrors the production integration shape: the procurement system POSTs a
requisition (plus a pointer to the uploaded attachment) and receives a structured
PO creation decision back. Run with::

    uvicorn po_creation.api.app:app --reload

Then POST to /create-po (see /docs for the interactive schema).
"""

from __future__ import annotations

import os

from fastapi import FastAPI

from ..config import DEFAULT_CONFIG
from ..pipeline import POCreationPipeline
from ..schemas import POCreationResult, PurchaseRequisition

TRUSTED_DIR = os.getenv("PO_TRUSTED_DIR", "data/trusted_sources")

app = FastAPI(
    title="Automated PO Creation",
    version="1.0.0",
    description="Auto-generate purchase orders from unstructured vendor documents.",
)

_pipeline: POCreationPipeline | None = None


def get_pipeline() -> POCreationPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = POCreationPipeline(trusted_dir=TRUSTED_DIR, config=DEFAULT_CONFIG)
    return _pipeline


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "backend": DEFAULT_CONFIG.extraction_backend}


@app.post("/create-po", response_model=POCreationResult)
def create_po(pr: PurchaseRequisition) -> POCreationResult:
    """Process one requisition and return the PO creation decision + full audit trail."""
    return get_pipeline().run(pr)
