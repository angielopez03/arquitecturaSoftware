from dataclasses import dataclass
from typing import Any, Dict, List

from backend.domain.ports.range_repository import RangeRepository


@dataclass(frozen=True)
class EspecieCatalogo:
    nombre: str
    rangos: Dict[str, Any]

    def __getitem__(self, item):
        if item in ("nombre", "name"):
            return self.nombre
        if item in ("rangos", "ranges"):
            return self.rangos
        raise KeyError(item)

    def __contains__(self, item):
        return item in ("nombre", "name", "rangos", "ranges")


class ListSpeciesService:
    """
    Caso de uso: Listar especies soportadas y sus rangos de referencia (RF5).
    Pertenece a la Capa de Aplicación (RA3).

    Responsabilidades:
    - Consultar el catálogo de especies a través del puerto RangeRepository (RA5 / DIP).
    - Exponer la lista estructurada de especies y sus rangos.

    Restricciones respetadas:
    - RA3: Vive en la capa de aplicación como orquestador.
    - RA4: No importa nada de Flask, jsonify, HTTP ni CSV.
    - RA5: Depende exclusivamente de la abstracción RangeRepository declarada en el dominio.
    - SRP: Su única razón de cambio es la consulta y exposición del catálogo de especies.
    """

    def __init__(self, repository: RangeRepository):
        self._repository = repository

    def ejecutar(self) -> List[EspecieCatalogo]:
        """
        Retorna la lista de especies con sus rangos de referencia (RF5).
        """
        all_species = self._repository.get_all_species()
        result: List[EspecieCatalogo] = []

        mapeo_nombres = {
            "humidity": "humedad",
            "light": "luz",
            "temperature": "temperatura",
        }

        for species_name, ranges in sorted(all_species.items()):
            rangos_adaptados: Dict[str, Any] = {}
            for param, rango in ranges.items():
                nombre_es = mapeo_nombres.get(param, param)
                rangos_adaptados[nombre_es] = rango
                rangos_adaptados[param] = rango

            result.append(
                EspecieCatalogo(
                    nombre=species_name,
                    rangos=rangos_adaptados,
                )
            )

        return result

    def execute(self) -> List[EspecieCatalogo]:
        return self.ejecutar()


# Alias en español para máxima compatibilidad
ListarEspecies = ListSpeciesService
