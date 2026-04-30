# Limitations

AegisFlow is a simulation, not a production streaming platform. The current version is designed to make the workflow inspectable without private infrastructure or proprietary data.

## Current Boundaries

- Events are synthetic and generated from fixed distributions.
- The dashboard simulates streaming in the browser.
- The Aegis Score is heuristic and transparent, not a trained predictive model.
- Financial exposure is estimated from event fields rather than downstream accounting systems.
- Pipeline health checks are modeled as lightweight validation logic.
- Mitigation actions are recommendations, not automated infrastructure changes.

## What Would Need to Change in Production

- Replace synthetic events with real producers and schemas.
- Add durable streaming infrastructure and event storage.
- Calibrate thresholds using historical incidents and false-positive review.
- Track model and data drift over time.
- Add service ownership, alert routing, and escalation policies.
- Require approval boundaries for high-impact automated actions.

These limits are deliberate for the public version of the project. They keep the demo reproducible while leaving a clear path toward a larger implementation.

