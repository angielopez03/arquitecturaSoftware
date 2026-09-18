"""
Controlador REST de diagnosticos (capa de presentacion).

Responde exclusivamente JSON (RA1). No contiene logica de negocio: traduce
HTTP -> dominio con el DTO, delega en el caso de uso, y traduce dominio -> JSON.

El blueprint se construye por funcion y recibe el caso de uso por parametro,
en vez de leerlo de current_app.config: asi el controlador no depende del
contenedor de Flask y las dependencias siguen viniendo del composition root.
"""
from flask import Blueprint, jsonify, request

from backend.domain.errors import ParametroInvalido
from backend.presentation.dto.diagnostico_request import DiagnosticoRequest
from backend.presentation.dto.diagnostico_response import diagnostico_a_json


def crear_blueprint_diagnosticos(diagnosticar_planta) -> Blueprint:
    bp = Blueprint("diagnosticos", __name__, url_prefix="/api/v1")

    @bp.post("/diagnosticos")
    def crear_diagnostico():
        cuerpo = request.get_json(silent=True)
        if cuerpo is None:
            raise ParametroInvalido("cuerpo", "se esperaba un cuerpo JSON valido")

        peticion = DiagnosticoRequest.desde_json(cuerpo)
        diagnostico = diagnosticar_planta.ejecutar(peticion.especie, peticion.medicion)
        return jsonify(diagnostico_a_json(diagnostico)), 200

    return bp
