from __future__ import annotations

from dataclasses import dataclass
from math import log1p
from statistics import mean


EVENT_WEIGHTS = {
    "transaction": 1.05,
    "login": 0.95,
    "infrastructure": 1.15,
    "external": 0.85,
    "finance": 1.1,
}

REGION_WEIGHTS = {
    "AMR": 1.0,
    "EMEIA": 0.92,
    "APAC": 0.98,
    "GC": 1.08,
}


@dataclass(frozen=True)
class RiskEvent:
    event_type: str
    region: str
    severity: float
    confidence: float
    financial_exposure: float
    impacted_services: int
    data_quality: float = 0.98

    def normalized(self) -> "RiskEvent":
        return RiskEvent(
            event_type=self.event_type,
            region=self.region,
            severity=_clamp(self.severity),
            confidence=_clamp(self.confidence),
            financial_exposure=max(0.0, self.financial_exposure),
            impacted_services=max(0, self.impacted_services),
            data_quality=_clamp(self.data_quality),
        )


@dataclass(frozen=True)
class AegisScore:
    score: int
    severity_band: str
    estimated_loss: float
    confidence: float
    drivers: tuple[str, ...]


def score_event(event: RiskEvent) -> AegisScore:
    clean = event.normalized()
    exposure_component = min(1.0, log1p(clean.financial_exposure) / log1p(600_000))
    service_component = min(1.0, clean.impacted_services / 9)
    type_weight = EVENT_WEIGHTS.get(clean.event_type, 1.0)
    region_weight = REGION_WEIGHTS.get(clean.region, 1.0)
    quality_penalty = 1 + max(0.0, 0.96 - clean.data_quality)

    raw_score = (
        42 * clean.severity
        + 24 * clean.confidence
        + 20 * exposure_component
        + 14 * service_component
    )
    score = round(min(100, raw_score * type_weight * region_weight * quality_penalty))
    estimated_loss = clean.financial_exposure * (0.25 + clean.severity * 0.75)

    return AegisScore(
        score=score,
        severity_band=_band(score),
        estimated_loss=round(estimated_loss, 2),
        confidence=round(clean.confidence, 3),
        drivers=_drivers(clean, exposure_component, service_component),
    )


def score_portfolio(events: list[RiskEvent]) -> AegisScore:
    if not events:
        return AegisScore(
            score=0,
            severity_band="clear",
            estimated_loss=0,
            confidence=0,
            drivers=("No active risk signals.",),
        )

    scored = [score_event(event) for event in events]
    top = sorted(scored, key=lambda item: item.score, reverse=True)[:5]
    score = round(max(item.score for item in top) * 0.62 + mean(item.score for item in top) * 0.38)
    loss = sum(item.estimated_loss for item in scored)
    confidence = mean(item.confidence for item in scored)
    drivers = tuple(driver for item in top for driver in item.drivers[:1])

    return AegisScore(
        score=min(100, score),
        severity_band=_band(score),
        estimated_loss=round(loss, 2),
        confidence=round(confidence, 3),
        drivers=drivers[:5],
    )


def _drivers(event: RiskEvent, exposure_component: float, service_component: float) -> tuple[str, ...]:
    drivers: list[str] = []
    if event.severity >= 0.75:
        drivers.append("High anomaly severity")
    if event.confidence >= 0.82:
        drivers.append("Strong model confidence")
    if exposure_component >= 0.7:
        drivers.append("Meaningful financial exposure")
    if service_component >= 0.45:
        drivers.append("Multiple services affected")
    if event.data_quality < 0.96:
        drivers.append("Data quality drift")
    if not drivers:
        drivers.append("Low but notable signal")
    return tuple(drivers)


def _band(score: int) -> str:
    if score >= 82:
        return "critical"
    if score >= 62:
        return "elevated"
    if score >= 36:
        return "watch"
    if score > 0:
        return "low"
    return "clear"


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

