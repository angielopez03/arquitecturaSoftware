from dataclasses import dataclass


@dataclass(frozen=True)
class Plant:
    """Entidad que representa la planta a evaluar."""
    name: str
    plant_type: str


@dataclass(frozen=True)
class Measurement:
    """
    Representa una lectura de indicadores en un momento dado.
    No importa si vino de un formulario manual o de un sensor IoT.
    """
    humidity: float
    light: float
    temperature: float
