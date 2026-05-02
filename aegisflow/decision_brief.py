from __future__ import annotations

from collections import Counter
from typing import Any


def build_decision_brief(summary: dict[str, Any]) -> dict[str, Any]:
    """Translate pipeline output into an operator-friendly decision brief."""
    portfolio = summary.get("portfolio", {})
    events = list(summary.get("events", []))
    health = list(summary.get("health", []))
    anomalies = list(summary.get("anomalies", []))

    score = int(portfolio.get("score", 0))
    band = str(portfolio.get("severity_band", "clear"))
    failed_checks = [item for item in health if not item.get("passed", False)]
    flagged_anomalies = [item for item in anomalies if item.get("is_anomaly", False)]
    top_events = sorted(
        events,
        key=lambda item: int(item.get("aegis_score", 0)),
        reverse=True,
    )[:3]

    regions = Counter(str(item.get("region", "unknown")) for item in top_events)
    event_types = Counter(str(item.get("event_type", "unknown")) for item in top_events)

    return {
        "headline": _headline(score, band, failed_checks),
        "risk_level": band,
        "portfolio_score": score,
        "estimated_loss": float(portfolio.get("estimated_loss", 0)),
        "confidence": float(portfolio.get("confidence", 0)),
        "primary_region": _most_common(regions),
        "primary_signal": _most_common(event_types),
        "evidence": _evidence(portfolio, failed_checks, flagged_anomalies, top_events),
        "recommended_actions": _recommended_actions(score, failed_checks, flagged_anomalies),
        "watch_items": _watch_items(top_events, failed_checks),
    }


def _headline(score: int, band: str, failed_checks: list[dict[str, Any]]) -> str:
    if score >= 82:
        return "Critical risk state: immediate operator review recommended."
    if failed_checks:
        return "Elevated risk with pipeline health checks requiring attention."
    if score >= 62:
        return "Elevated risk state: monitor top drivers and prepare mitigation."
    if score >= 36:
        return "Watch state: signals are rising but remain below escalation threshold."
    return f"{band.title()} risk state: no immediate escalation recommended."


def _evidence(
    portfolio: dict[str, Any],
    failed_checks: list[dict[str, Any]],
    flagged_anomalies: list[dict[str, Any]],
    top_events: list[dict[str, Any]],
) -> list[str]:
    evidence = [
        f"Portfolio Aegis Score is {portfolio.get('score', 0)} with {portfolio.get('severity_band', 'clear')} severity.",
        f"Estimated financial exposure is ${float(portfolio.get('estimated_loss', 0)):,.0f}.",
    ]

    drivers = list(portfolio.get("drivers", []))[:2]
    if drivers:
        evidence.append("Top score drivers: " + ", ".join(str(driver) for driver in drivers) + ".")
    if failed_checks:
        evidence.append(f"{len(failed_checks)} pipeline health check(s) failed.")
    if flagged_anomalies:
        evidence.append(f"{len(flagged_anomalies)} event(s) crossed the local anomaly threshold.")
    if top_events:
        event = top_events[0]
        evidence.append(
            "Highest-risk event is "
            f"{event.get('event_type', 'unknown')} in {event.get('region', 'unknown')} "
            f"with score {event.get('aegis_score', 0)}."
        )

    return evidence


def _recommended_actions(
    score: int,
    failed_checks: list[dict[str, Any]],
    flagged_anomalies: list[dict[str, Any]],
) -> list[str]:
    actions: list[str] = []
    if score >= 82:
        actions.append("Open an incident review and freeze automated threshold changes.")
        actions.append("Validate the highest-exposure events before mitigation is automated.")
    elif score >= 62:
        actions.append("Monitor the top event drivers and prepare a mitigation plan.")
    else:
        actions.append("Continue monitoring and keep the current thresholds active.")

    if failed_checks:
        actions.append("Review failed pipeline health checks before trusting downstream automation.")
    if flagged_anomalies:
        actions.append("Compare anomaly flags against recent baseline behavior to reduce false positives.")

    return actions


def _watch_items(top_events: list[dict[str, Any]], failed_checks: list[dict[str, Any]]) -> list[str]:
    items = [
        f"{event.get('event_type', 'unknown')} signal in {event.get('region', 'unknown')} "
        f"(score {event.get('aegis_score', 0)})"
        for event in top_events
    ]
    items.extend(str(check.get("check_name", "pipeline health")) for check in failed_checks)
    return items[:5]


def _most_common(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return counter.most_common(1)[0][0]
