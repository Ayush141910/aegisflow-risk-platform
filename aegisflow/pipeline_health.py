from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    check_name: str
    passed: bool
    observed: float
    threshold: float
    action: str


def validate_batch(events: list[dict]) -> list[ValidationResult]:
    if not events:
        return [
            ValidationResult(
                check_name="batch_not_empty",
                passed=False,
                observed=0,
                threshold=1,
                action="Hold scoring job and replay last healthy micro-batch.",
            )
        ]

    quality_values = [float(event.get("data_quality", 0)) for event in events]
    missing_scores = sum(1 for event in events if "aegis_score" not in event)
    avg_quality = sum(quality_values) / len(quality_values)

    return [
        ValidationResult(
            check_name="avg_data_quality",
            passed=avg_quality >= 0.955,
            observed=round(avg_quality, 4),
            threshold=0.955,
            action="Route affected source to quarantine and keep previous model threshold.",
        ),
        ValidationResult(
            check_name="missing_score_rate",
            passed=(missing_scores / len(events)) <= 0.01,
            observed=round(missing_scores / len(events), 4),
            threshold=0.01,
            action="Backfill scores from deterministic rules before publishing dashboard update.",
        ),
    ]

