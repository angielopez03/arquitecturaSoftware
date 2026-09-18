"""
Manejadores de error (capa de presentacion).

Unico lugar del sistema que conoce codigos HTTP. Los errores del dominio
NO saben que existe HTTP: los lanzan como excepciones de negocio y aqui
se traducen a 400 / 404 con el cuerpo uniforme que exige RF6.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException

from backend.domain.errors import EspecieNoSoportada, ParametroInvalido


def cuerpo_error(codigo: str, mensaje: str, detalle: dict = None):
    return {"error": codigo, "mensaje": mensaje, "detalle": detalle or {}}


def registrar_manejadores(app):
    @app.errorhandler(EspecieNoSoportada)
    def _especie_no_soportada(e):
        return jsonify(cuerpo_error(
            "ESPECIE_NO_SOPORTADA",
            f"La especie '{e.especie}' no esta en la tabla de referencia.",
            {"especie": e.especie},
        )), 404

    @app.errorhandler(ParametroInvalido)
    def _parametro_invalido(e):
        return jsonify(cuerpo_error(
            "PARAMETRO_INVALIDO",
            f"El parametro '{e.campo}' es invalido: {e.motivo}.",
            {"campo": e.campo},
        )), 400

    @app.errorhandler(HTTPException)
    def _http(e):
        codigos = {404: "RUTA_NO_ENCONTRADA", 405: "METODO_NO_PERMITIDO"}
        mensajes = {
            404: "La ruta solicitada no existe en esta API.",
            405: "El metodo HTTP no esta permitido en esta ruta.",
        }
        return jsonify(cuerpo_error(
            codigos.get(e.code, "PETICION_NO_ATENDIDA"),
            mensajes.get(e.code, "La peticion no pudo atenderse."),
        )), e.code

    @app.errorhandler(Exception)
    def _inesperado(e):
        app.logger.exception("error inesperado")
        return jsonify(cuerpo_error(
            "ERROR_INTERNO",
            "Ocurrio un error inesperado procesando la peticion.",
        )), 500
