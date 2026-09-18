import math
from dataclasses import dataclass

from backend.domain.errors import ValorFisicamenteImposible


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
                raise ValorFisicamenteImposible(nombre, valor, "debe ser numerico")
            if not math.isfinite(valor):
                raise ValorFisicamenteImposible(nombre, valor, "debe ser finito")

        if not 0 <= self.humedad <= 100:
            raise ValorFisicamenteImposible(
                "humedad", self.humedad, "debe estar entre 0 y 100"
            )
        if self.luz < 0:
            raise ValorFisicamenteImposible("luz", self.luz, "no puede ser negativa")
        if self.temperatura < -50:
            raise ValorFisicamenteImposible(
                "temperatura", self.temperatura, "no puede ser menor que -50"
            )