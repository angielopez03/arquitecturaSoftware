from typing import Dict

from backend.domain.model.entities import Plant, Measurement
from backend.domain.model.enums import IndicatorLevel, PlantStatus
from backend.domain.ports.range_repository import RangeRepository
from backend.domain.rules.indicator_evaluator import IndicatorEvaluator


class DiagnosisService:
    """
    Caso de uso principal. Orquesta la evaluacion de cada indicador
    y determina el diagnostico final de la planta.

    Depende de la ABSTRACCION RangeRepository, no de CSVRangeRepository.
    Esto es Inversion de Dependencias (DIP): quien decida que
    repositorio concreto usar se inyecta desde afuera (app.py).
    """

    def __init__(self, repository: RangeRepository, evaluator: IndicatorEvaluator):
        self._repository = repository
        self._evaluator = evaluator

    def diagnose(self, plant: Plant, measurement: Measurement) -> dict:
        ranges = self._repository.get_ranges(plant.plant_type)

        levels: Dict[str, IndicatorLevel] = {
            "humidity": self._evaluator.evaluate(measurement.humidity, ranges["humidity"]),
            "light": self._evaluator.evaluate(measurement.light, ranges["light"]),
            "temperature": self._evaluator.evaluate(measurement.temperature, ranges["temperature"]),
        }

        status = self._determine_status(levels)

        return {
            "plant_name": plant.name,
            "plant_type": plant.plant_type,
            "levels": levels,
            "status": status,
        }

    @staticmethod
    def _determine_status(levels: Dict[str, IndicatorLevel]) -> PlantStatus:
        values = list(levels.values())

        if all(level == IndicatorLevel.OPTIMO for level in values):
            return PlantStatus.SALUDABLE

        if any(level == IndicatorLevel.BAJO for level in values):
            return PlantStatus.CRITICO

        return PlantStatus.EN_RIESGO
