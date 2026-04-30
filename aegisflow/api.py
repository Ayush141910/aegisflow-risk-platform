from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .event_generator import generate_events
from .pipeline import SAMPLE_PATH, replay_incident, score_event_payload, summarize_events

APP_DIR = Path(__file__).resolve().parent.parent / "app"


app = FastAPI(
    title="AegisFlow API",
    version="0.2.0",
    description="Local API for the AegisFlow risk intelligence pipeline.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_sample_events() -> list[dict]:
    if SAMPLE_PATH.exists():
        return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    return generate_events(count=32, seed=17, incident_start=12, incident_end=18)


@app.get("/api/events")
def get_events() -> dict:
    events = _load_sample_events()
    return {"count": len(events), "events": events}


@app.get("/api/score")
def get_score() -> dict:
    return summarize_events(_load_sample_events())["portfolio"]


@app.get("/api/health")
def get_health() -> dict:
    return {"checks": summarize_events(_load_sample_events())["health"]}


@app.get("/api/anomalies")
def get_anomalies() -> dict:
    return {"anomalies": summarize_events(_load_sample_events())["anomalies"]}


@app.get("/api/summary")
def get_summary() -> dict:
    return summarize_events(_load_sample_events())


@app.post("/api/events/score")
def post_score_event(event: dict) -> dict:
    return score_event_payload(event)


@app.post("/api/incidents/replay")
def post_replay_incident() -> dict:
    return replay_incident()


@app.get("/api")
def root() -> dict:
    return {
        "service": "AegisFlow API",
        "endpoints": [
            "/api/events",
            "/api/score",
            "/api/health",
            "/api/anomalies",
            "/api/summary",
            "/api/incidents/replay",
        ],
    }


app.mount("/", StaticFiles(directory=APP_DIR, html=True), name="dashboard")
