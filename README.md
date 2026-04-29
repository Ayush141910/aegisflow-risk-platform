# AegisFlow

AegisFlow is a local simulation of a real-time risk intelligence platform. It streams synthetic business events, scores operational risk, explains the top drivers, estimates financial exposure, and recommends mitigation actions from a control-room style dashboard.

## Overview

The project connects four parts of a risk and resilience workflow:

- data engineering reliability
- machine-learning anomaly detection
- business impact forecasting
- decision support for operations and finance

The runtime is intentionally lightweight so the demo can run locally without cloud infrastructure. The design still follows the same responsibilities a production system would need: ingest events, validate data quality, score risk, explain the score, and trigger a response.

## Demo

Open the dashboard:

```bash
python3 -m http.server 8000 --directory app
```

Then visit:

```text
http://localhost:8000
```

You can also open `app/index.html` directly in a browser.

What to try:

- click `Simulate Incident`
- switch between `Live` and `Replay`
- pause and resume the stream
- click a region on the risk map
- watch the Aegis Score, pipeline health, driver summary, and mitigation queue change together

## Capabilities

- Replays transaction, login, infrastructure, finance, and external-event signals.
- Calculates an Aegis Score from severity, model confidence, financial exposure, impacted services, region, and data quality.
- Surfaces explainability drivers instead of showing a mystery score.
- Estimates financial exposure so the alert has business context.
- Models pipeline health checks for schema quality, stream lag, and model freshness.
- Recommends mitigation actions such as replay validation, threshold locking, and traffic shifting.

## Repository Layout

```text
app/
  index.html        Interactive control-room dashboard
  styles.css        Responsive dashboard styling
  main.js           Streaming simulation and browser-side scoring
aegisflow/
  risk_engine.py    Aegis Score implementation
  event_generator.py
  pipeline_health.py
tests/
  test_risk_engine.py
docs/
  architecture.md
```

## Local Commands

Generate deterministic sample events:

```bash
python3 -m aegisflow.event_generator --count 240 --out data/events.json
```

Run tests:

```bash
python3 -m unittest discover -s tests
```

Start the dashboard:

```bash
python3 -m http.server 8000 --directory app
```

## Design Notes

The initial scoring model is intentionally transparent. In an operational dashboard, the model output needs to be explainable enough for an operator or business partner to understand why a signal changed and what action is recommended.

The current dashboard uses a browser-side event simulator so it can run without Docker, cloud credentials, Kafka, or Spark. The Python package contains the same scoring logic in a testable form, which keeps the scoring behavior separate from the UI.

In a production version, the local simulator would become:

- Kafka or Redpanda for event ingestion
- Spark Structured Streaming for feature windows and scoring
- Delta Lake or Iceberg for historical event storage
- Great Expectations for validation suites
- MLflow for experiment tracking and model registry
- Airflow for scheduled recovery, retraining, and backfill jobs
- a warehouse or serving store for dashboard queries
