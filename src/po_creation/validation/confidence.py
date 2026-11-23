"""Confidence aggregation and the PO creation decision.

This is the policy layer that converts (extraction confidence + validation
report) into one of: AUTO_CREATE, NEEDS_REVIEW, REJECTED. The whole system's
safety/automation trade-off is concentrated in these few rules, which is exactly
where you want it — easy to read, easy to audit, easy to tune.
"""

from __future__ import annotations

from ..config import PipelineConfig
from ..schemas import (
    ExtractionResult,
    POCreationDecision,
    POCreationResult,
    ValidationReport,
)


def decide(
    extraction: ExtractionResult,
    validation: ValidationReport,
    config: PipelineConfig,
) -> POCreationResult:
    # Overall confidence starts from the weakest extracted field (a chain is only
    # as strong as its weakest link), then each SOFT issue applies a penalty.
    base = extraction.min_confidence()
    penalty = (1 - config.soft_issue_penalty) ** validation.soft_issue_count
    overall = round(base * penalty, 4)

    if validation.has_hard_failure:
        hard_codes = sorted(
            {i.code for i in validation.issues if i.severity.name == "HARD"}
        )
        decision = POCreationDecision.NEEDS_REVIEW
        rationale = (
            "Routed to review: hard validation failure(s): "
            + ", ".join(hard_codes)
        )
    elif overall >= config.auto_create_threshold:
        decision = POCreationDecision.AUTO_CREATE
        rationale = (
            f"Auto-created: confidence {overall:.3f} >= "
            f"threshold {config.auto_create_threshold:.3f} and no hard failures."
        )
    else:
        decision = POCreationDecision.NEEDS_REVIEW
        rationale = (
            f"Routed to review: confidence {overall:.3f} < "
            f"threshold {config.auto_create_threshold:.3f}."
        )

    return POCreationResult(
        pr_number=extraction.pr_number,
        decision=decision,
        overall_confidence=overall,
        extraction=extraction,
        validation=validation,
        rationale=rationale,
    )
