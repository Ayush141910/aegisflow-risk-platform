# Incident Walkthrough

This walkthrough describes a representative incident replay in AegisFlow. The data is synthetic, but the sequence mirrors the type of operational workflow the platform is designed to support.

## Scenario

A regional login anomaly appears during a normal traffic window. The signal is not enough by itself to prove abuse or an outage, but it coincides with elevated infrastructure latency and lower data quality from one source.

The platform should answer four questions quickly:

- What changed?
- How confident is the signal?
- What business or service impact might it create?
- What response should happen next?

## Event Sequence

1. Login events in `APAC` begin scoring above their normal baseline.
2. The same window shows an increase in impacted services from one to four.
3. Data quality drops below the normal threshold, which increases uncertainty.
4. The Aegis Score moves from `watch` to `elevated`.
5. The dashboard recommends replay validation, increased sampling, and owner notification.

## Why the Score Moves

The score is designed to be explainable rather than purely predictive. In this scenario, the largest contributors are:

- high anomaly severity
- strong model confidence
- multiple services affected
- data quality drift
- meaningful financial exposure

The goal is not to claim that the score is a final truth. The goal is to make the event actionable enough for triage.

## Expected Operator Response

For an elevated incident, the platform recommends bounded mitigation:

- replay the last healthy micro-batch before publishing downstream metrics
- temporarily increase sampling for the affected signal family
- notify the service owner with the top score drivers
- avoid automatic threshold changes until data quality recovers

The self-healing behavior is intentionally visible. AegisFlow should not hide uncertainty or silently repair over a real incident.

## Current Limitations

The replay uses generated events and heuristic scoring. A production system would need calibrated thresholds, real service ownership metadata, historical baselines, model monitoring, and a clear escalation policy.

