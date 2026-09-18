import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Medicion:
    humedad: float
    luz: float
    temperatura: float

    def __post_init__(self):
        valores = {
            "humedad": self.humedad,
            "luz": self.luz,
            "temperatura": self.temperatura,
        }

        for nombre, valor in valores.items():
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise ValueError(f"{nombre} debe ser numerico")
            if not math.isfinite(valor):
                raise ValueError(f"{nombre} debe ser finito")

        if not 0 <= self.humedad <= 100:
            raise ValueError("la humedad debe estar entre 0 y 100")
        if self.luz < 0:
            raise ValueError("la luz no puede ser negativa")
        if self.temperatura < -50:
            raise ValueError("la temperatura no puede ser menor que -50")