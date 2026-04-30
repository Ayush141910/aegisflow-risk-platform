from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev

from .features import build_feature_matrix, event_to_features


@dataclass(frozen=True)
class AnomalyResult:
    event_id: str
    is_anomaly: bool
    anomaly_score: float
    top_features: tuple[str, ...]
    model: str


class RobustAnomalyDetector:
    """Small local anomaly detector with no external service dependency.

    The detector prefers explainability over cleverness: it learns baseline means
    and standard deviations, then scores events by average positive z-score.
    """

    def __init__(self) -> None:
        self.feature_names: list[str] = []
        self.means: list[float] = []
        self.stdevs: list[float] = []

    def fit(self, events: list[dict]) -> "RobustAnomalyDetector":
        matrix, feature_names = build_feature_matrix(events)
        self.feature_names = feature_names
        if not matrix:
            self.means = []
            self.stdevs = []
            return self

        columns = list(zip(*matrix))
        self.means = [mean(column) for column in columns]
        self.stdevs = [pstdev(column) or 1.0 for column in columns]
        return self

    def score(self, event: dict) -> AnomalyResult:
        if not self.feature_names:
            raise ValueError("Detector must be fit before scoring events.")

        features = event_to_features(event)
        values = [features[name] for name in self.feature_names]
        zscores = [
            max(0.0, (value - baseline) / spread)
            for value, baseline, spread in zip(values, self.means, self.stdevs)
        ]
        weighted = sum(zscores) / max(1, len(zscores))
        anomaly_score = round(min(1.0, weighted / 1.8), 3)
        ranked = sorted(
            zip(self.feature_names, zscores),
            key=lambda item: item[1],
            reverse=True,
        )
        top_features = tuple(name for name, score in ranked if score > 0.75)[:3]

        return AnomalyResult(
            event_id=str(event.get("id", "")),
            is_anomaly=anomaly_score >= 0.58,
            anomaly_score=anomaly_score,
            top_features=top_features or ("severity",),
            model="robust_zscore",
        )

    def score_many(self, events: list[dict]) -> list[AnomalyResult]:
        return [self.score(event) for event in events]


def detect_anomalies(events: list[dict], baseline_size: int = 12) -> list[AnomalyResult]:
    if not events:
        return []

    baseline = events[: max(1, min(baseline_size, len(events)))]
    detector = RobustAnomalyDetector().fit(baseline)
    return detector.score_many(events)

