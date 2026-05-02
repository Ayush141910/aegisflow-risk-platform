import unittest

from aegisflow.decision_brief import build_decision_brief
from aegisflow.event_generator import generate_events
from aegisflow.pipeline import score_event_payload, summarize_events


class PipelineTest(unittest.TestCase):
    def test_summary_contains_pipeline_outputs(self):
        events = generate_events(count=24, seed=17, incident_start=8, incident_end=14)

        summary = summarize_events(events)

        self.assertIn("portfolio", summary)
        self.assertIn("health", summary)
        self.assertIn("anomalies", summary)
        self.assertEqual(len(summary["events"]), 24)

    def test_score_event_payload_returns_drivers(self):
        event = generate_events(count=1, seed=5)[0]

        scored = score_event_payload(event)

        self.assertIn("score", scored)
        self.assertIn("drivers", scored)

    def test_decision_brief_contains_actions_and_evidence(self):
        events = generate_events(count=32, seed=17, incident_start=12, incident_end=18)

        brief = build_decision_brief(summarize_events(events))

        self.assertIn("headline", brief)
        self.assertIn("recommended_actions", brief)
        self.assertIn("evidence", brief)
        self.assertGreater(len(brief["recommended_actions"]), 0)


if __name__ == "__main__":
    unittest.main()
