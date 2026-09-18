from abc import ABC, abstractmethod
from typing import Dict

from backend.domain.model.rango import Rango, Range


class ProveedorRangos(ABC):
    """
    Puerto del dominio para obtener rangos de referencia por especie (RA5 / DIP).

    La implementacion concreta puede leer un CSV, una base de datos o
    cualquier otra fuente sin que el dominio conozca ese detalle.
    """

    @abstractmethod
    def obtener_rangos(self, especie: str) -> Dict[str, Rango]:
        raise NotImplementedError


class RangeRepository(ProveedorRangos):
    """
    Contrato del repositorio de rangos en el dominio.
    Soporta tanto la interfaz en español (obtener_rangos) como
    en inglés (get_ranges, get_all_species) para interoperabilidad total.
    """

    @abstractmethod
    def get_ranges(self, plant_type: str) -> Dict[str, Rango]:
        raise NotImplementedError

    def obtener_rangos(self, especie: str) -> Dict[str, Rango]:
        return self.get_ranges(especie)

    @abstractmethod
    def get_all_species(self) -> Dict[str, Dict[str, Rango]]:
        """
        Retorna el catálogo completo de especies y sus rangos de referencia (RF5).
        """
        raise NotImplementedError

    def obtener_todas_las_especies(self) -> Dict[str, Dict[str, Rango]]:
        return self.get_all_species()
