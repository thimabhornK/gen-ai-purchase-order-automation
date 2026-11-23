"""Automated PO Creation — GenAI purchase-order automation (clean-room, synthetic-data demo).

Public API:

    from po_creation import POCreationPipeline, PurchaseRequisition
    from po_creation.config import PipelineConfig
"""

from .config import DEFAULT_CONFIG, PipelineConfig
from .pipeline import POCreationPipeline
from .schemas import (
    Currency,
    POCreationDecision,
    POCreationResult,
    PurchaseRequisition,
)

__version__ = "1.0.0"
__all__ = [
    "POCreationPipeline",
    "PipelineConfig",
    "DEFAULT_CONFIG",
    "PurchaseRequisition",
    "POCreationResult",
    "POCreationDecision",
    "Currency",
]
