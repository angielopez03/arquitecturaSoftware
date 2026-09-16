from abc import ABC, abstractmethod

from models.entities import Measurement


class InputProvider(ABC):
    """
    Interfaz (contrato) para obtener una Measurement, sin importar
    si viene de un formulario web manual o de un sensor IoT.
    """

    @abstractmethod
    def get_measurement(self, raw_data: dict) -> Measurement:
        raise NotImplementedError


class ManualInputProvider(InputProvider):
    """
    Implementacion concreta: convierte datos crudos de un
    formulario HTML (dict de strings) en una Measurement.

    Para soportar un sensor IoT: crear SensorInputProvider(InputProvider)
    en este mismo archivo/paquete y cambiar una linea en app.py.
    """

    def get_measurement(self, raw_data: dict) -> Measurement:
        return Measurement(
            humidity=float(raw_data["humidity"]),
            light=float(raw_data["light"]),
            temperature=float(raw_data["temperature"]),
        )
