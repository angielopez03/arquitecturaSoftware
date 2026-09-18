from abc import ABC, abstractmethod
from typing import Mapping

from backend.domain.errors import ParametroInvalido
from backend.domain.model.enums import IndicatorLevel, PlantStatus


class ReglaAgregacion(ABC):
    """Contrato para convertir niveles individuales en un estado global."""

    @abstractmethod
    def agregar(self, niveles: Mapping[str, IndicatorLevel]) -> PlantStatus:
        raise NotImplementedError


class ReglaPorDesviaciones(ReglaAgregacion):
    """
    Clasifica la planta por la cantidad de indicadores fuera de rango.

    Un solo indicador fuera del rango implica riesgo y dos o mas implican
    estado critico. Esta regla conserva los tres estados globales del
    dominio y funciona igual aunque se agreguen indicadores como pH.
    """

    def agregar(self, niveles: Mapping[str, IndicatorLevel]) -> PlantStatus:
        if not niveles:
            raise ParametroInvalido(
                "niveles", "se necesita al menos un indicador para agregar"
            )

        desviaciones = sum(
            nivel != IndicatorLevel.OPTIMO for nivel in niveles.values()
        )
        if desviaciones == 0:
            return PlantStatus.SALUDABLE
        if desviaciones == 1:
            return PlantStatus.EN_RIESGO
        return PlantStatus.CRITICO