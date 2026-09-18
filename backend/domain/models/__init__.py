"""Módulo puente de compatibilidad retroactiva.
La ruta canónica del dominio es `backend.domain.model` (singular).
"""
from backend.domain.model.entities import Plant, Planta, Measurement, Medicion
from backend.domain.model.enums import IndicatorLevel, PlantStatus
from backend.domain.model.rango import Rango, Range
from backend.domain.model.diagnostico import Diagnostico, ParametroDiagnostico

__all__ = [
    "Plant",
    "Planta",
    "Measurement",
    "Medicion",
    "IndicatorLevel",
    "PlantStatus",
    "Rango",
    "Range",
    "Diagnostico",
    "ParametroDiagnostico",
]
