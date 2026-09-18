from dataclasses import dataclass

from backend.domain.model.medicion import Medicion, Measurement


@dataclass(frozen=True)
class Plant:
    """Entidad que representa la planta a evaluar."""
    name: str
    plant_type: str


Planta = Plant

__all__ = ["Plant", "Planta", "Medicion", "Measurement"]
