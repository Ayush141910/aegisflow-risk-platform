import unittest

from aegisflow.anomaly_model import RobustAnomalyDetector
from aegisflow.event_generator import generate_events


class AnomalyModelTest(unittest.TestCase):
    def test_detector_flags_high_exposure_event(self):
        baseline = generate_events(count=16, seed=3, incident_start=100, incident_end=110)
        detector = RobustAnomalyDetector().fit(baseline)
        event = {
            **baseline[0],
            "id": "evt-hot",
            "severity": 0.96,
            "confidence": 0.94,
            "financial_exposure": 450_000,
            "impacted_services": 7,
            "data_quality": 0.91,
        }

        result = detector.score(event)

        self.assertTrue(result.is_anomaly)
        self.assertGreaterEqual(result.anomaly_score, 0.58)
        self.assertTrue(result.top_features)


if __name__ == "__main__":
    unittest.main()

