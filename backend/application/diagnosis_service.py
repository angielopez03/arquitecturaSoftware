from typing import Dict, List, Union

from backend.domain.models.entities import Measurement, Plant
from backend.domain.models.enums import IndicatorLevel, PlantStatus
from backend.domain.ports.range_repository import RangeRepository
from backend.domain.rules.indicator_evaluator import IndicatorEvaluator


class DiagnosisService:
    """
    Caso de uso principal (Capa de Aplicación - RA3).
    Orquesta la evaluación de cada indicador y determina el diagnóstico final de la planta.
    """

    def __init__(self, repository: RangeRepository, evaluator: IndicatorEvaluator):
        self._repository = repository
        self._evaluator = evaluator

    def diagnose(self, plant: Union[Plant, str], measurement: Measurement) -> dict:
        """
        Ejecuta el diagnóstico de la planta a partir de sus mediciones.
        """
        if isinstance(plant, str):
            plant = Plant(name=plant, plant_type=plant)

        ranges = self._repository.get_ranges(plant.plant_type)

        levels: Dict[str, IndicatorLevel] = {
            "humidity": self._evaluator.evaluate(measurement.humidity, ranges["humidity"]),
            "light": self._evaluator.evaluate(measurement.light, ranges["light"]),
            "temperature": self._evaluator.evaluate(measurement.temperature, ranges["temperature"]),
        }

        status = self._determine_status(levels)
        recommendations = self._generate_recommendations(levels, ranges)

        return {
            "plant_name": plant.name,
            "plant_type": plant.plant_type,
            "levels": levels,
            "status": status,
            "recommendations": recommendations,
        }

    @staticmethod
    def _determine_status(levels: Dict[str, IndicatorLevel]) -> PlantStatus:
        values = list(levels.values())

        if all(level == IndicatorLevel.OPTIMO for level in values):
            return PlantStatus.SALUDABLE

        out_of_range = [level for level in values if level != IndicatorLevel.OPTIMO]
        if len(out_of_range) >= 2 or any(level == IndicatorLevel.BAJO for level in values):
            return PlantStatus.CRITICO

        return PlantStatus.EN_RIESGO

    @staticmethod
    def _generate_recommendations(levels: Dict[str, IndicatorLevel], ranges: dict) -> List[str]:
        recs: List[str] = []
        for param, level in levels.items():
            r = ranges.get(param)
            r_str = f"({r.min_value} - {r.max_value})" if r else ""
            if level == IndicatorLevel.BAJO:
                recs.append(f"El parámetro '{param}' está por debajo del rango recomendado {r_str}: aumentar el nivel o suministro.")
            elif level == IndicatorLevel.ALTO:
                recs.append(f"El parámetro '{param}' está por encima del rango recomendado {r_str}: reducir el nivel o proteger la planta.")
        return recs
