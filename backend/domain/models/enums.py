from enum import Enum


class IndicatorLevel(str, Enum):
    """Nivel de un indicador individual (humedad, luz o temperatura)."""
    BAJO = "BAJO"
    MEDIO = "MEDIO"
    OPTIMO = "OPTIMO"
    ALTO = "ALTO"


class PlantStatus(str, Enum):
    """Diagnostico final de la planta."""
    SALUDABLE = "SALUDABLE"
    EN_RIESGO = "EN_RIESGO"
    CRITICO = "CRITICO"
