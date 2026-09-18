"""Capa de Infraestructura (RA3).
Contiene adaptadores para persistencia (CSV), entrada manual y configuración externa.
Depende exclusivamente de los puertos declarados en el Dominio (RA5 / DIP).
"""
from backend.infrastructure.csv_range_repository import CSVRangeRepository
from backend.infrastructure.input_provider import InputProvider, ManualInputProvider

__all__ = [
    "CSVRangeRepository",
    "InputProvider",
    "ManualInputProvider",
]
