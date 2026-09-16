from models.enums import IndicatorLevel
from models.value_objects import Range

MEDIO_THRESHOLD_RATIO = 0.20


class IndicatorEvaluator:
    """
    Responsabilidad unica (SRP): decidir el IndicatorLevel
    de un valor dado su Range optimo.
    """

    def evaluate(self, value: float, optimal_range: Range) -> IndicatorLevel:
        if optimal_range.contains(value):
            return IndicatorLevel.OPTIMO

        ratio = optimal_range.distance_ratio(value)
        if ratio <= MEDIO_THRESHOLD_RATIO:
            return IndicatorLevel.MEDIO

        return IndicatorLevel.BAJO
