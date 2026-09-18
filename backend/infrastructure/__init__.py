"""Capa de Infraestructura (RA3).
Contiene adaptadores de persistencia y configuración externa.
Depende exclusivamente de los puertos declarados en el Dominio (RA5 / DIP).
"""
from backend.infrastructure.csv_range_repository import CSVRangeRepository
from backend.infrastructure.config import Config

__all__ = [
    "CSVRangeRepository",
    "Config",
]
