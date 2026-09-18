from typing import Dict, List, Union

from backend.domain.model.entities import Measurement, Plant
from backend.domain.model.enums import IndicatorLevel, PlantStatus
from backend.domain.model.medicion import Medicion
from backend.domain.model.diagnostico import Diagnostico, ParametroDiagnostico
from backend.domain.rules.aggregation_rule import ReglaPorDesviaciones
from backend.domain.ports.range_repository import RangeRepository
from backend.domain.rules.indicator_evaluator import IndicatorEvaluator


class DiagnosisService:
    """
    Caso de uso principal (Capa de Aplicación - RA3).
    Orquesta la evaluación de cada indicador y determina el diagnóstico final de la planta.
    No tiene conocimiento de HTTP, frameworks ni transporte (RA4).
    """

    def __init__(self, repository: RangeRepository, evaluator: IndicatorEvaluator):
        self._repository = repository
        self._evaluator = evaluator
        self._regla_agregacion = ReglaPorDesviaciones()

    def ejecutar(self, especie: str, medicion: Medicion) -> Diagnostico:
        """
        Ejecuta el caso de uso retornando la entidad Diagnostico del dominio (RF1-RF4).
        Utilizado por los controladores REST de la capa de presentación (Anexo A).
        """
        rangos = self._repository.obtener_rangos(especie)

        valores = {
            "humedad": medicion.humedad,
            "luz": medicion.luz,
            "temperatura": medicion.temperatura,
        }

        # RF2: Evaluar cada parámetro contra el rango óptimo
        niveles: Dict[str, IndicatorLevel] = {}
        parametros: List[ParametroDiagnostico] = []

        mapeo_claves = {
            "humedad": ("humedad", "humidity"),
            "luz": ("luz", "light"),
            "temperatura": ("temperatura", "temperature"),
        }

        for param_nombre in ("humedad", "luz", "temperatura"):
            val = valores[param_nombre]
            claves = mapeo_claves[param_nombre]
            rango = next((rangos[k] for k in claves if k in rangos), None)
            if rango is None:
                raise KeyError(f"No se encontró rango para {param_nombre} en la especie {especie}")

            nivel = self._evaluator.evaluate(val, rango)
            niveles[param_nombre] = nivel
            parametros.append(
                ParametroDiagnostico(
                    nombre=param_nombre,
                    valor=val,
                    rango=rango,
                    nivel=nivel,
                )
            )

        # RF3: Derivar estado global de la planta según regla de agregación
        estado = self._regla_agregacion.agregar(niveles)

        return Diagnostico(
            especie=especie,
            estado=estado,
            parametros=tuple(parametros),
        )

    def diagnose(self, plant: Union[Plant, str], measurement: Measurement) -> dict:
        """
        Método compatible que retorna el diccionario para vistas o clientes tradicionales.
        """
        if isinstance(plant, str):
            plant = Plant(name=plant, plant_type=plant)

        especie = plant.plant_type
        # Si measurement es Medicion, tiene .humedad o .humidity
        medicion = measurement if isinstance(measurement, Medicion) else Medicion(
            humidity=measurement.humidity,
            light=measurement.light,
            temperature=measurement.temperature,
        )

        diagnostico = self.ejecutar(especie, medicion)

        niveles_dict = {
            "humidity": next(p.nivel for p in diagnostico.parametros if p.nombre == "humedad"),
            "light": next(p.nivel for p in diagnostico.parametros if p.nombre == "luz"),
            "temperature": next(p.nivel for p in diagnostico.parametros if p.nombre == "temperatura"),
        }

        return {
            "plant_name": plant.name,
            "plant_type": plant.plant_type,
            "levels": niveles_dict,
            "status": diagnostico.estado,
            "recommendations": list(diagnostico.recomendaciones),
        }


# Alias bilingüe para el caso de uso
DiagnosticarPlanta = DiagnosisService
