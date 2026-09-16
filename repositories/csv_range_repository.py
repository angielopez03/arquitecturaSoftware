import csv
from typing import Dict

from repositories.range_repository import RangeRepository
from models.value_objects import Range


class CSVRangeRepository(RangeRepository):
    """
    Implementacion concreta de RangeRepository que lee los
    rangos desde un archivo CSV.

    Para migrar a base de datos: crear SQLRangeRepository(RangeRepository)
    en este mismo paquete y cambiar una linea en app.py.
    """

    def __init__(self, csv_path: str):
        self._csv_path = csv_path
        self._cache: Dict[str, Dict[str, Range]] = None

    def _load(self) -> Dict[str, Dict[str, Range]]:
        if self._cache is not None:
            return self._cache

        data: Dict[str, Dict[str, Range]] = {}
        with open(self._csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                plant_type = row["plant_type"].strip().lower()
                data[plant_type] = {
                    "humidity": Range(float(row["humidity_min"]), float(row["humidity_max"])),
                    "light": Range(float(row["light_min"]), float(row["light_max"])),
                    "temperature": Range(float(row["temperature_min"]), float(row["temperature_max"])),
                }
        self._cache = data
        return data

    def get_ranges(self, plant_type: str) -> Dict[str, Range]:
        data = self._load()
        key = plant_type.strip().lower()
        return data.get(key, data["default"])
