# Design Log

## Why the First Version Is Local

The first version runs locally because the main product question is independent of infrastructure size: can noisy operational signals be turned into a clear risk state, explanation, and mitigation recommendation?

Using a local simulator keeps the project easy to inspect and run. The same boundaries can later map to Kafka, Spark Structured Streaming, Delta Lake, Airflow, Great Expectations, and MLflow.

## Why the Aegis Score Is Transparent

The score blends:

- anomaly severity
- model confidence
- estimated financial exposure
- impacted service count
- regional weighting
- data quality penalty

This is intentionally more transparent than a black-box model. Operational users need to understand why a score changed before they trust an automated recommendation.

## Why the Dashboard Prioritizes Explanation

The dashboard is not only an alert surface. It is designed to show:

- the current risk level
- the trend over time
- regional concentration
- top score drivers
- pipeline health
- recommended next actions

This keeps the workflow centered on decision support instead of raw anomaly labels.

## Synthetic Data Tradeoff

Synthetic data makes the project reproducible and safe to publish. The tradeoff is that the event distribution is simpler than a real production system.

The sample generator intentionally creates a short incident wave so the scoring behavior can be inspected without needing private data or external services.

## Production Path

The local pieces are shaped so they can be replaced incrementally:

```text
event generator        -> Kafka or Redpanda producers
browser replay         -> streaming API or warehouse-backed service
risk_engine.py         -> Spark Structured Streaming scoring job
sample JSON            -> Delta Lake or Iceberg event table
pipeline_health.py     -> Great Expectations suites
manual incident button -> Airflow recovery and replay DAGs
```

## Open Questions

- How should thresholds differ by event family and region?
- What is the acceptable false-positive rate for each business partner?
- Which mitigations should be automatic, and which should require human approval?
- How should missing or delayed data affect the displayed score?
- What monitoring should exist for drift in both model behavior and source data quality?

