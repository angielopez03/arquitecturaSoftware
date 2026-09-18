from enum import Enum


class IndicatorLevel(str, Enum):
    """Nivel de un indicador: carencia, rango optimo o exceso."""
    BAJO = "BAJO"
    OPTIMO = "OPTIMO"
    ALTO = "ALTO"


class PlantStatus(str, Enum):
    """Diagnostico final de la planta."""
    SALUDABLE = "SALUDABLE"
    EN_RIESGO = "EN_RIESGO"
    CRITICO = "CRITICO"
