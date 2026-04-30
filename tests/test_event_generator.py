import unittest
from datetime import datetime, timezone

from aegisflow.event_generator import generate_events


class EventGeneratorTest(unittest.TestCase):
    def test_generation_is_reproducible(self):
        start = datetime(2026, 1, 15, 14, 0, tzinfo=timezone.utc)

        first = generate_events(count=8, seed=17, start=start, incident_start=3, incident_end=4)
        second = generate_events(count=8, seed=17, start=start, incident_start=3, incident_end=4)

        self.assertEqual(first, second)

    def test_custom_incident_window_creates_elevated_events(self):
        events = generate_events(count=20, seed=17, incident_start=6, incident_end=12)

        self.assertTrue(any(event["aegis_score"] >= 62 for event in events[6:13]))


if __name__ == "__main__":
    unittest.main()

