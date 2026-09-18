import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Rango:
    minimo: float
    maximo: float

    def __post_init__(self):
        if any(
            isinstance(valor, bool)
            or not isinstance(valor, (int, float))
            or not math.isfinite(valor)
            for valor in (self.minimo, self.maximo)
        ):
            raise ValueError("los limites del rango deben ser numeros finitos")
        if self.minimo > self.maximo:
            raise ValueError("el limite minimo no puede superar al maximo")

    def contiene(self, valor: float) -> bool:
        return self.minimo <= valor <= self.maximo

    def proporcion_distancia(self, valor: float) -> float:
        amplitud = self.maximo - self.minimo
        if amplitud == 0:
            return 0.0
        if valor < self.minimo:
            return (self.minimo - valor) / amplitud
        if valor > self.maximo:
            return (valor - self.maximo) / amplitud
        return 0.0

    @property
    def min_value(self) -> float:
        return self.minimo

    @property
    def max_value(self) -> float:
        return self.maximo

    def contains(self, value: float) -> bool:
        return self.contiene(value)

    def distance_ratio(self, value: float) -> float:
        return self.proporcion_distancia(value)


# Alias para interoperabilidad con código en inglés
Range = Rango