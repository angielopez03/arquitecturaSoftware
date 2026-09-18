from typing import Mapping

from backend.domain.errors import ParametroInvalido
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

    def evaluate_collection(
        self,
        values: Mapping[str, float],
        optimal_ranges: Mapping[str, object],
    ) -> dict[str, IndicatorLevel]:
        nombres_valores = set(values)
        nombres_rangos = set(optimal_ranges)
        if nombres_valores != nombres_rangos:
            faltantes = sorted(nombres_rangos - nombres_valores)
            sobrantes = sorted(nombres_valores - nombres_rangos)
            raise ParametroInvalido(
                "indicadores",
                f"colecciones incompatibles; faltantes={faltantes}, sobrantes={sobrantes}",
            )

        return {
            nombre: self.evaluate(values[nombre], optimal_ranges[nombre])
            for nombre in optimal_ranges
        }
