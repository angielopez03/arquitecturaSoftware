"""
Controlador REST del catalogo de especies (RF5).

Es la fuente que alimenta el selector del front: el HTML no escribe
ninguna especie a mano.
"""
from flask import Blueprint, jsonify

from backend.presentation.dto.diagnostico_response import especies_a_json


def crear_blueprint_especies(listar_especies) -> Blueprint:
    bp = Blueprint("especies", __name__, url_prefix="/api/v1")

    @bp.get("/especies")
    def listar():
        return jsonify(especies_a_json(listar_especies.ejecutar())), 200

    return bp
