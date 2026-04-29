# AegisFlow

AegisFlow is a local simulation of a real-time risk intelligence platform. It streams synthetic business events, scores operational risk, explains the top drivers, estimates financial exposure, and recommends mitigation actions from one control-room style dashboard.

I built it to explore a question that shows up in a lot of data roles: how do you turn noisy, ambiguous signals into a decision someone can actually use?

## Why This Project

The goal was not to build the biggest possible stack. The goal was to connect four things that are usually discussed separately:

- data engineering reliability
- machine-learning anomaly detection
- business impact forecasting
- decision support for operations and finance

The first version keeps the runtime lightweight so the demo is easy to run, but the design mirrors the same responsibilities a production platform would have: ingest events, validate data quality, score risk, explain the score, and trigger a response.

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

## What It Does

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

## Design Decisions

I kept the first model intentionally simple. The harder part of this project was not picking a fancy algorithm; it was making the signal usable: detect risk quickly, explain why it matters, connect it to business impact, and show what action should happen next.

The current dashboard uses a browser-side event simulator so anyone can run it without Docker, cloud credentials, Kafka, or Spark. The Python package contains the same scoring logic in a testable form, which makes it easier to discuss how the platform would move from demo to production.

In a production version, the local simulator would become:

- Kafka or Redpanda for event ingestion
- Spark Structured Streaming for feature windows and scoring
- Delta Lake or Iceberg for historical event storage
- Great Expectations for validation suites
- MLflow for experiment tracking and model registry
- Airflow for scheduled recovery, retraining, and backfill jobs
- a warehouse or serving store for dashboard queries

## Interview Talking Points

- How I designed the Aegis Score and why it blends severity, confidence, exposure, data quality, and service impact.
- Why explainability matters more than raw anomaly labels in an operational dashboard.
- How false positives would affect business partners and how thresholds should be tuned.
- What I would change when moving from synthetic events to real event streams.
- How self-healing behavior should be bounded so automation does not hide a real incident.

## Resume Bullet

Built AegisFlow, a real-time risk intelligence platform simulation that streams operational and business events, scores anomaly severity, forecasts financial exposure, validates pipeline health, and recommends mitigation actions through an interactive dashboard.
