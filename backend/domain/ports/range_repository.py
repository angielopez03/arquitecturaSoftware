from abc import ABC, abstractmethod
from typing import Dict

from backend.domain.model.rango import Rango


class ProveedorRangos(ABC):
    """
    Puerto del dominio para obtener rangos de referencia por especie.

    La implementacion concreta puede leer un CSV, una base de datos o
    cualquier otra fuente sin que el dominio conozca ese detalle.
    """

    @abstractmethod
    def obtener_rangos(self, especie: str) -> Dict[str, Rango]:
        raise NotImplementedError


class RangeRepository(ProveedorRangos):
    """Adaptador temporal para el contrato anterior de infraestructura."""

    @abstractmethod
    def get_ranges(self, plant_type: str) -> Dict[str, Rango]:
        raise NotImplementedError

    def obtener_rangos(self, especie: str) -> Dict[str, Rango]:
        return self.get_ranges(especie)
