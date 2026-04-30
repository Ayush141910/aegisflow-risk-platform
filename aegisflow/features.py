from __future__ import annotations

import math


EVENT_TYPES = ["transaction", "login", "infrastructure", "external", "finance"]
REGIONS = ["AMR", "EMEIA", "APAC", "GC"]


def event_to_features(event: dict) -> dict[str, float]:
    exposure = max(0.0, float(event.get("financial_exposure", 0)))
    impacted = max(0.0, float(event.get("impacted_services", 0)))
    features = {
        "severity": _clamp(float(event.get("severity", 0))),
        "confidence": _clamp(float(event.get("confidence", 0))),
        "log_exposure": math.log1p(exposure),
        "impacted_services": min(1.0, impacted / 9),
        "data_quality_gap": max(0.0, 1.0 - _clamp(float(event.get("data_quality", 0)))),
    }

    event_type = str(event.get("event_type", ""))
    region = str(event.get("region", ""))
    for value in EVENT_TYPES:
        features[f"event_type_{value}"] = 1.0 if event_type == value else 0.0
    for value in REGIONS:
        features[f"region_{value}"] = 1.0 if region == value else 0.0

    return features


def build_feature_matrix(events: list[dict]) -> tuple[list[list[float]], list[str]]:
    feature_dicts = [event_to_features(event) for event in events]
    feature_names = list(feature_dicts[0].keys()) if feature_dicts else []
    matrix = [[features[name] for name in feature_names] for features in feature_dicts]
    return matrix, feature_names


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

