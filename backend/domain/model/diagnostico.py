from dataclasses import dataclass

from backend.domain.model.enums import IndicatorLevel, PlantStatus
from backend.domain.model.rango import Rango


@dataclass(frozen=True)
class ParametroDiagnostico:
    nombre: str
    valor: float
    rango: Rango
    nivel: IndicatorLevel

    @property
    def recomendacion(self) -> str:
        if self.nivel == IndicatorLevel.OPTIMO:
            return ""

        accion = "Aumentar" if self.nivel == IndicatorLevel.BAJO else "Reducir"
        return (
            f"{accion} el parametro {self.nombre} hasta el rango optimo "
            f"({self.rango.minimo} - {self.rango.maximo})."
        )


@dataclass(frozen=True)
class Diagnostico:
    especie: str
    estado: PlantStatus
    parametros: tuple[ParametroDiagnostico, ...]

    def __post_init__(self):
        object.__setattr__(self, "parametros", tuple(self.parametros))

    @property
    def recomendaciones(self) -> tuple[str, ...]:
        return tuple(
            parametro.recomendacion
            for parametro in self.parametros
            if parametro.nivel != IndicatorLevel.OPTIMO
        )