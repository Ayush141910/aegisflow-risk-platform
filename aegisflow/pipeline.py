from __future__ import annotations

from pathlib import Path

from .anomaly_model import detect_anomalies
from .event_generator import generate_events
from .pipeline_health import validate_batch
from .risk_engine import RiskEvent, score_event, score_portfolio


SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_events.json"


def normalize_event(event: dict) -> RiskEvent:
    return RiskEvent(
        event_type=str(event.get("event_type", "")),
        region=str(event.get("region", "")),
        severity=float(event.get("severity", 0)),
        confidence=float(event.get("confidence", 0)),
        financial_exposure=float(event.get("financial_exposure", 0)),
        impacted_services=int(event.get("impacted_services", 0)),
        data_quality=float(event.get("data_quality", 0.98)),
    )


def score_event_payload(event: dict) -> dict:
    scored = score_event(normalize_event(event))
    return {
        "event_id": event.get("id", ""),
        "score": scored.score,
        "severity_band": scored.severity_band,
        "estimated_loss": scored.estimated_loss,
        "confidence": scored.confidence,
        "drivers": list(scored.drivers),
    }


def summarize_events(events: list[dict]) -> dict:
    scored_events = [score_event(normalize_event(event)) for event in events]
    portfolio = score_portfolio([normalize_event(event) for event in events])
    health = validate_batch(events)
    anomalies = detect_anomalies(events)
    anomaly_by_id = {item.event_id: item for item in anomalies}
    enriched = []

    for event, scored in zip(events, scored_events):
        anomaly = anomaly_by_id.get(str(event.get("id", "")))
        enriched.append(
            {
                **event,
                "aegis_score": scored.score,
                "severity_band": scored.severity_band,
                "estimated_loss": scored.estimated_loss,
                "drivers": list(scored.drivers),
                "anomaly": {
                    "is_anomaly": anomaly.is_anomaly if anomaly else False,
                    "anomaly_score": anomaly.anomaly_score if anomaly else 0,
                    "top_features": list(anomaly.top_features) if anomaly else [],
                    "model": anomaly.model if anomaly else "none",
                },
            }
        )

    return {
        "portfolio": {
            "score": portfolio.score,
            "severity_band": portfolio.severity_band,
            "estimated_loss": portfolio.estimated_loss,
            "confidence": portfolio.confidence,
            "drivers": list(portfolio.drivers),
        },
        "health": [
            {
                "check_name": item.check_name,
                "passed": item.passed,
                "observed": item.observed,
                "threshold": item.threshold,
                "action": item.action,
            }
            for item in health
        ],
        "anomalies": [
            {
                "event_id": item.event_id,
                "is_anomaly": item.is_anomaly,
                "anomaly_score": item.anomaly_score,
                "top_features": list(item.top_features),
                "model": item.model,
            }
            for item in anomalies
        ],
        "events": enriched,
    }


def replay_incident(count: int = 48, seed: int = 17) -> dict:
    events = generate_events(
        count=count,
        seed=seed,
        incident_start=18,
        incident_end=28,
    )
    return summarize_events(events)

