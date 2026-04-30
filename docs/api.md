# API Reference

AegisFlow includes a local FastAPI service for the full pipeline mode. The static dashboard still works without the API, but the backend makes the event, validation, anomaly detection, and scoring pipeline inspectable.

Start the API:

```bash
pip install -r requirements.txt
uvicorn aegisflow.api:app --reload
```

Open the dashboard:

```text
http://localhost:8000
```

Open the API docs:

```text
http://localhost:8000/docs
```

## Endpoints

### `GET /api/events`

Returns the committed sample event set.

### `GET /api/summary`

Runs the local pipeline and returns portfolio risk, validation checks, anomaly scores, and enriched events.

Example response shape:

```json
{
  "portfolio": {
    "score": 78,
    "severity_band": "elevated",
    "estimated_loss": 214000.0,
    "confidence": 0.77,
    "drivers": ["Meaningful financial exposure"]
  },
  "health": [],
  "anomalies": [],
  "events": []
}
```

### `GET /api/score`

Returns the current portfolio-level Aegis Score.

### `GET /api/health`

Returns validation checks for the active event batch.

### `GET /api/anomalies`

Returns local anomaly detection results.

### `POST /api/events/score`

Scores a single event payload.

### `POST /api/incidents/replay`

Generates a deterministic incident replay and returns the pipeline summary.

This endpoint is used by the dashboard when the API is running locally.

