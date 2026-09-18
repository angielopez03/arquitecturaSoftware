from backend.domain.models.enums import IndicatorLevel
from backend.domain.models.value_objects import Range

MEDIO_THRESHOLD_RATIO = 0.20


class IndicatorEvaluator:
    """
    Responsabilidad unica (SRP): decidir el IndicatorLevel
    de un valor dado su Range optimo (RF2).
    Distingue carencia (BAJO) de exceso (ALTO).
    """

    def evaluate(self, value: float, optimal_range: Range) -> IndicatorLevel:
        if optimal_range.contains(value):
            return IndicatorLevel.OPTIMO

        if value < optimal_range.min_value:
            return IndicatorLevel.BAJO

        return IndicatorLevel.ALTO
