# Design Log

## Why the First Version Is Local

The first version runs locally because the main product question is independent of infrastructure size: can noisy operational signals be turned into a clear risk state, explanation, and mitigation recommendation?

Using a local simulator keeps the project easy to inspect and run. The same boundaries can later map to Kafka, Spark Structured Streaming, Delta Lake, Airflow, Great Expectations, and MLflow.

## Why Add a Local API

The dashboard can run as a static GitHub Pages demo, but the full project benefits from an inspectable backend. The FastAPI service exposes the same pipeline stages that the dashboard summarizes: events, validation checks, anomaly detection, risk scoring, and incident replay.

That split keeps the public demo easy to open while giving the repository a real system boundary for technical review.

## Why the Aegis Score Is Transparent

The score blends:

- anomaly severity
- model confidence
- estimated financial exposure
- impacted service count
- regional weighting
- data quality penalty

This is intentionally more transparent than a black-box model. Operational users need to understand why a score changed before they trust an automated recommendation.

## Why the Anomaly Detector Is Lightweight

The local anomaly detector uses a learned baseline and robust z-score style scoring. That choice is deliberate: the project does not have real incident labels, and a simple transparent model is easier to reason about than an overfit classifier.

The detector is not meant to be the final production model. It provides a concrete ML stage that can be inspected, tested, and replaced.

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
features.py            -> feature pipeline or feature store
anomaly_model.py       -> calibrated anomaly model
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
