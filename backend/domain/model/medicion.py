import math
from dataclasses import dataclass
from typing import Optional

from backend.domain.errors import ValorFisicamenteImposible


@dataclass(frozen=True)
class Medicion:
    humedad: float
    luz: float
    temperatura: float

    def __init__(
        self,
        humedad: Optional[float] = None,
        luz: Optional[float] = None,
        temperatura: Optional[float] = None,
        humidity: Optional[float] = None,
        light: Optional[float] = None,
        temperature: Optional[float] = None,
    ):
        h = humedad if humedad is not None else humidity
        l = luz if luz is not None else light
        t = temperatura if temperatura is not None else temperature

        object.__setattr__(self, "humedad", h)
        object.__setattr__(self, "luz", l)
        object.__setattr__(self, "temperatura", t)
        self.__post_init__()

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

    @property
    def humidity(self) -> float:
        return self.humedad

    @property
    def light(self) -> float:
        return self.luz

    @property
    def temperature(self) -> float:
        return self.temperatura


# Alias bilingüe para compatibilidad
Measurement = Medicion