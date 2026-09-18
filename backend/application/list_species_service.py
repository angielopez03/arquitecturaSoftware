from typing import Any, Dict, List

from backend.domain.ports.range_repository import RangeRepository


class ListSpeciesService:
    """
    Caso de uso: Listar especies soportadas y sus rangos de referencia (RF5).
    Pertenece a la Capa de Aplicación (RA3).

    Responsabilidades:
    - Consultar el catálogo de especies a través del puerto RangeRepository (RA5 / DIP).
    - Exponer la lista estructurada de especies y sus rangos en objetos estándar de Python.

    Restricciones respetadas:
    - RA3: Vive en la capa de aplicación como orquestador.
    - RA4: No importa nada de Flask, jsonify, HTTP ni CSV.
    - RA5: Depende exclusivamente de la abstracción RangeRepository declarada en el dominio.
    - SRP: Su única razón de cambio es la consulta y exposición del catálogo de especies.
    """

    def __init__(self, repository: RangeRepository):
        self._repository = repository

    def execute(self) -> List[Dict[str, Any]]:
        """
        Ejecuta el caso de uso para listar las especies disponibles y sus rangos de referencia (RF5).

        :return: Lista de diccionarios con el nombre de la especie y los rangos de cada parámetro.
                 Estructura compatible con el contrato de API del Anexo A:
                 [
                     {
                         "nombre": "sansevieria",
                         "rangos": {
                             "humedad": [20.0, 45.0],
                             "luz": [200.0, 1500.0],
                             "temperatura": [15.0, 29.0]
                         }
                     },
                     ...
                 ]
        """
        all_species = self._repository.get_all_species()
        result: List[Dict[str, Any]] = []

        param_translations = {
            "humidity": "humedad",
            "light": "luz",
            "temperature": "temperatura",
        }

        for species_name, ranges in sorted(all_species.items()):
            rangos_dict: Dict[str, List[float]] = {}
            for param, rango in ranges.items():
                interval = [rango.min_value, rango.max_value]
                rangos_dict[param] = interval
                # Soporte para nombres en español del Anexo A
                if param in param_translations:
                    rangos_dict[param_translations[param]] = interval

            species_data = {
                "nombre": species_name,
                "name": species_name,
                "rangos": rangos_dict,
                "ranges": rangos_dict,
            }
            result.append(species_data)

        return result


# Alias en español para máxima compatibilidad con el enunciado
ListarEspecies = ListSpeciesService
