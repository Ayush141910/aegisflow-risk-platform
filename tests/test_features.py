import unittest

from aegisflow.features import build_feature_matrix, event_to_features


class FeatureTest(unittest.TestCase):
    def test_event_to_features_encodes_core_fields(self):
        event = {
            "event_type": "login",
            "region": "APAC",
            "severity": 0.8,
            "confidence": 0.9,
            "financial_exposure": 100_000,
            "impacted_services": 4,
            "data_quality": 0.93,
        }

        features = event_to_features(event)

        self.assertEqual(features["event_type_login"], 1.0)
        self.assertEqual(features["region_APAC"], 1.0)
        self.assertGreater(features["log_exposure"], 0)
        self.assertGreater(features["data_quality_gap"], 0)

    def test_build_feature_matrix_returns_stable_columns(self):
        matrix, names = build_feature_matrix(
            [
                {"event_type": "login", "region": "AMR"},
                {"event_type": "finance", "region": "GC"},
            ]
        )

        self.assertEqual(len(matrix), 2)
        self.assertIn("event_type_login", names)
        self.assertEqual(len(matrix[0]), len(names))


if __name__ == "__main__":
    unittest.main()

