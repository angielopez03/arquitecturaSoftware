"""
DTO de entrada (capa de presentacion).

Responsabilidad unica: traducir el cuerpo JSON de una peticion HTTP en
objetos del dominio. Es el punto exacto donde se cumple RA6: despues de
esta clase, nadie mas ve un dict crudo.

Esta clase valida PRESENCIA y TIPO. La validacion de plausibilidad fisica
(humedad 0-100, etc.) NO esta aqui: vive en el constructor de Medicion,
porque es una regla de negocio, no una regla de transporte.
"""
from dataclasses import dataclass

from backend.domain.errors import ParametroInvalido
from backend.domain.model.medicion import Medicion

CAMPOS_NUMERICOS = ("humedad", "luz", "temperatura")


@dataclass(frozen=True)
class DiagnosticoRequest:
    especie: str
    medicion: Medicion

    @staticmethod
    def desde_json(cuerpo) -> "DiagnosticoRequest":
        if not isinstance(cuerpo, dict):
            raise ParametroInvalido("cuerpo", "se esperaba un objeto JSON")

        especie = cuerpo.get("especie")
        if not isinstance(especie, str) or not especie.strip():
            raise ParametroInvalido("especie", "parametro ausente o vacio")

        valores = {}
        for campo in CAMPOS_NUMERICOS:
            if campo not in cuerpo or cuerpo[campo] is None or cuerpo[campo] == "":
                raise ParametroInvalido(campo, "parametro ausente")
            valores[campo] = _a_numero(campo, cuerpo[campo])

        # Medicion valida los limites fisicos y lanza ValorFisicamenteImposible
        return DiagnosticoRequest(especie=especie.strip().lower(), medicion=Medicion(**valores))


def _a_numero(campo: str, valor) -> float:
    if isinstance(valor, bool):
        raise ParametroInvalido(campo, "valor no numerico")
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, str):
        try:
            return float(valor.strip().replace(",", "."))
        except ValueError:
            raise ParametroInvalido(campo, "valor no numerico")
    raise ParametroInvalido(campo, "valor no numerico")
