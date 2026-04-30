import unittest


try:
    from fastapi.testclient import TestClient

    from aegisflow.api import app
except (ImportError, RuntimeError):
    TestClient = None
    app = None


@unittest.skipIf(TestClient is None, "FastAPI is not installed")
class ApiTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_summary_endpoint(self):
        response = self.client.get("/api/summary")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("portfolio", body)
        self.assertIn("events", body)

    def test_replay_endpoint(self):
        response = self.client.post("/api/incidents/replay")

        self.assertEqual(response.status_code, 200)
        self.assertIn("anomalies", response.json())


if __name__ == "__main__":
    unittest.main()
