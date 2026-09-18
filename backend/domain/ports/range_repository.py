from abc import ABC, abstractmethod
from typing import Dict

from backend.domain.models.value_objects import Range


class RangeRepository(ABC):
    """
    Interfaz (contrato) para obtener los rangos de referencia
    de un tipo de planta. Los servicios dependen de ESTA clase,
    nunca de una implementacion concreta (DIP de SOLID).

    Para agregar una nueva fuente de datos (base de datos, API),
    se crea una nueva clase que herede de RangeRepository e
    implemente get_ranges(). No hay que tocar nada mas.
    """

    @abstractmethod
    def get_ranges(self, plant_type: str) -> Dict[str, Range]:
        raise NotImplementedError

    @abstractmethod
    def get_all_species(self) -> Dict[str, Dict[str, Range]]:
        """
        Retorna el catálogo completo de especies y sus rangos de referencia (RF5).
        """
        raise NotImplementedError
