import csv
import os
from typing import Dict, Optional

from backend.domain.ports.range_repository import RangeRepository
from backend.domain.models.value_objects import Range
from backend.domain.errors import EspecieNoSoportada


class CSVRangeRepository(RangeRepository):
    """
    Adaptador de infraestructura que implementa el puerto RangeRepository (RA5 / DIP).
    Lee los rangos de referencia ambientales desde un archivo plano CSV.

    Principios arquitectónicos demostrados:
    - RA5 / DIP: Implementa una abstracción definida en el Dominio (RangeRepository).
      La dependencia apunta de Infraestructura hacia el Dominio, nunca al revés.
      El Dominio y la Capa de Aplicación no tienen conocimiento de este archivo.
    - LSP (Sustitución de Liskov): Es 100% sustituible por SQLRangeRepository,
      un mock o cualquier otra fuente de datos sin afectar a los casos de uso.
    - H-07: Resuelve la ubicación incorrecta del puerto que existía en el diseño inicial.
    """

    def __init__(self, csv_path: str):
        self._csv_path = csv_path
        self._cache: Optional[Dict[str, Dict[str, Range]]] = None

    def _load(self) -> Dict[str, Dict[str, Range]]:
        if self._cache is not None:
            return self._cache

        if not os.path.exists(self._csv_path):
            raise FileNotFoundError(f"Archivo de rangos CSV no encontrado en la ruta: {self._csv_path}")

        data: Dict[str, Dict[str, Range]] = {}
        with open(self._csv_path, newline="", encoding="utf-8") as f:
            valid_lines = (line for line in f if line.strip() and not line.strip().startswith("#"))
            reader = csv.DictReader(valid_lines)
            for row in reader:
                if not row:
                    continue
                plant_type = (row.get("plant_type") or row.get("especie") or "").strip().lower()
                if not plant_type:
                    continue

                h_min = float(row.get("humidity_min") or row.get("humedad_min"))
                h_max = float(row.get("humidity_max") or row.get("humedad_max"))
                l_min = float(row.get("light_min") or row.get("luz_min"))
                l_max = float(row.get("light_max") or row.get("luz_max"))
                t_min = float(row.get("temperature_min") or row.get("temp_min"))
                t_max = float(row.get("temperature_max") or row.get("temp_max"))

                data[plant_type] = {
                    "humidity": Range(h_min, h_max),
                    "light": Range(l_min, l_max),
                    "temperature": Range(t_min, t_max),
                }

        self._cache = data
        return data

    def get_ranges(self, plant_type: str) -> Dict[str, Range]:
        """
        Obtiene los rangos de referencia para una especie específica.
        Lanza EspecieNoSoportada si la especie no está registrada (H-06 / RF6).
        """
        data = self._load()
        key = plant_type.strip().lower()
        if key not in data:
            raise EspecieNoSoportada(plant_type)
        return data[key]

    def get_all_species(self) -> Dict[str, Dict[str, Range]]:
        """
        Retorna todas las especies reales disponibles en el CSV (RF5).
        """
        return self._load()
