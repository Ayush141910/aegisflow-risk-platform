import unittest

from aegisflow.risk_engine import RiskEvent, score_event, score_portfolio


class RiskEngineTest(unittest.TestCase):
    def test_high_exposure_event_scores_critical(self):
        event = RiskEvent(
            event_type="infrastructure",
            region="GC",
            severity=0.93,
            confidence=0.94,
            financial_exposure=450_000,
            impacted_services=7,
            data_quality=0.94,
        )

        scored = score_event(event)

        self.assertGreaterEqual(scored.score, 82)
        self.assertEqual(scored.severity_band, "critical")
        self.assertIn("Meaningful financial exposure", scored.drivers)

    def test_portfolio_empty_state_is_clear(self):
        scored = score_portfolio([])

        self.assertEqual(scored.score, 0)
        self.assertEqual(scored.severity_band, "clear")

    def test_inputs_are_clamped(self):
        event = RiskEvent(
            event_type="login",
            region="AMR",
            severity=4,
            confidence=-2,
            financial_exposure=-100,
            impacted_services=-5,
            data_quality=3,
        )

        scored = score_event(event)

        self.assertGreaterEqual(scored.score, 0)
        self.assertLessEqual(scored.score, 100)


if __name__ == "__main__":
    unittest.main()

