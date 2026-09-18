from backend.domain.model.enums import IndicatorLevel


class IndicatorEvaluator:
    """
    Responsabilidad unica (SRP): decidir el IndicatorLevel
    de un valor dado su Range optimo.
    """

    def evaluate(self, value: float, optimal_range) -> IndicatorLevel:
        if hasattr(optimal_range, "minimo"):
            minimum = optimal_range.minimo
            maximum = optimal_range.maximo
        else:
            minimum = optimal_range.min_value
            maximum = optimal_range.max_value

        if value < minimum:
            return IndicatorLevel.BAJO
        if value > maximum:
            return IndicatorLevel.ALTO

        return IndicatorLevel.OPTIMO
