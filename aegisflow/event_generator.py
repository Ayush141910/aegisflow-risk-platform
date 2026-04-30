from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .risk_engine import RiskEvent, score_event


EVENT_TYPES = ["transaction", "login", "infrastructure", "external", "finance"]
REGIONS = ["AMR", "EMEIA", "APAC", "GC"]
SERVICES = [
    "payments",
    "identity",
    "device_activation",
    "fulfillment",
    "finance_close",
    "data_platform",
]

DEFAULT_START = datetime(2026, 1, 15, 14, 0, tzinfo=timezone.utc)


def generate_events(
    count: int = 240,
    seed: int = 7,
    start: datetime = DEFAULT_START,
    incident_start: int = 130,
    incident_end: int = 165,
) -> list[dict]:
    rng = random.Random(seed)
    events: list[dict] = []

    for index in range(count):
        event_type = rng.choice(EVENT_TYPES)
        region = rng.choice(REGIONS)
        incident_wave = incident_start <= index <= incident_end
        severity = rng.betavariate(2, 8)
        confidence = rng.uniform(0.52, 0.88)
        exposure = rng.uniform(4_000, 75_000)
        impacted = rng.randint(1, 3)
        data_quality = rng.uniform(0.965, 0.998)

        if incident_wave and event_type in {"transaction", "infrastructure", "login"}:
            severity = rng.uniform(0.72, 0.96)
            confidence = rng.uniform(0.81, 0.97)
            exposure = rng.uniform(110_000, 420_000)
            impacted = rng.randint(3, 7)
            data_quality = rng.uniform(0.91, 0.975)

        risk_event = RiskEvent(
            event_type=event_type,
            region=region,
            severity=severity,
            confidence=confidence,
            financial_exposure=exposure,
            impacted_services=impacted,
            data_quality=data_quality,
        )
        scored = score_event(risk_event)

        events.append(
            {
                "id": f"evt-{index + 1:04d}",
                "timestamp": (start + timedelta(minutes=index)).isoformat(),
                "event_type": event_type,
                "region": region,
                "service": rng.choice(SERVICES),
                "severity": round(severity, 3),
                "confidence": round(confidence, 3),
                "financial_exposure": round(exposure, 2),
                "impacted_services": impacted,
                "data_quality": round(data_quality, 3),
                "aegis_score": scored.score,
                "severity_band": scored.severity_band,
                "drivers": list(scored.drivers),
            }
        )

    return events


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic AegisFlow sample events.")
    parser.add_argument("--count", type=int, default=240)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--start", default=DEFAULT_START.isoformat())
    parser.add_argument("--incident-start", type=int, default=130)
    parser.add_argument("--incident-end", type=int, default=165)
    parser.add_argument("--out", type=Path, default=Path("data/events.json"))
    args = parser.parse_args()

    start = datetime.fromisoformat(args.start)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    events = generate_events(args.count, args.seed, start, args.incident_start, args.incident_end)
    args.out.write_text(json.dumps(events, indent=2), encoding="utf-8")
    print(f"Wrote {args.count} events to {args.out}")


if __name__ == "__main__":
    main()
