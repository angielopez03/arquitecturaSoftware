from dataclasses import dataclass


@dataclass(frozen=True)
class Range:
    """Rango optimo [min_value, max_value] para un indicador."""
    min_value: float
    max_value: float

    def contains(self, value: float) -> bool:
        return self.min_value <= value <= self.max_value

    def distance_ratio(self, value: float) -> float:
        span = self.max_value - self.min_value
        if span <= 0:
            return 0.0
        if value < self.min_value:
            return (self.min_value - value) / span
        if value > self.max_value:
            return (value - self.max_value) / span
        return 0.0
