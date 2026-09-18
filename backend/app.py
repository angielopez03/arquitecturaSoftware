from typing import Optional

from flask import Flask, jsonify

from backend.application.diagnosis_service import DiagnosisService
from backend.application.list_species_service import ListSpeciesService
from backend.domain.rules.indicator_evaluator import IndicatorEvaluator
from backend.infrastructure.config import Config
from backend.infrastructure.csv_range_repository import CSVRangeRepository
from backend.presentation.api.diagnostico_controller import crear_blueprint_diagnosticos
from backend.presentation.api.especies_controller import crear_blueprint_especies
from backend.presentation.errors.error_handlers import registrar_manejadores


def create_app(config: Optional[Config] = None) -> Flask:
    """
    Application Factory & Composition Root (RA3).
    Único punto del sistema donde se ensamblan las implementaciones concretas
    de las cuatro capas arquitectónicas.

    Responde exclusivamente con JSON (RA1).
    No renderiza plantillas HTML ni genera strings HTML en controladores.
    """
    cfg = config or Config.from_env()
    app = Flask(__name__)

    # --- Capa de Infraestructura (Adaptadores) ---
    # Escenario de sustentación (Migración CSV -> PostgreSQL):
    # Para cambiar a PostgreSQL, solo se reemplaza esta línea por:
    # range_repository = PostgresRangeRepository(cfg.db_connection_string)
    # y ninguna otra capa se modifica (RA5 / DIP / OCP).
    range_repository = CSVRangeRepository(cfg.csv_path)

    # --- Capa de Dominio (Reglas y Evaluadores) ---
    evaluator = IndicatorEvaluator()

    # --- Capa de Aplicación (Casos de Uso) ---
    diagnosis_service = DiagnosisService(repository=range_repository, evaluator=evaluator)
    list_species_service = ListSpeciesService(repository=range_repository)

    app.config["CONFIG"] = cfg
    app.config["DIAGNOSIS_SERVICE"] = diagnosis_service
    app.config["LIST_SPECIES_SERVICE"] = list_species_service

    # --- Capa de Presentación (Controladores REST y Manejo de Errores) ---
    app.register_blueprint(crear_blueprint_diagnosticos(diagnosis_service))
    app.register_blueprint(crear_blueprint_especies(list_species_service))
    registrar_manejadores(app)

    @app.route("/", methods=["GET"])
    def index():
        """
        Endpoint raíz de la API (RA1).
        Responde exclusivamente con JSON con metadatos del servicio.
        """
        return jsonify({
            "servicio": "Matera Inteligente API",
            "version": "v1",
            "estado": "activo",
            "endpoints": {
                "diagnosticos": "/api/v1/diagnosticos",
                "especies": "/api/v1/especies",
            },
        }), 200

    # --- Configuración de CORS (RA7 / H-14) ---
    try:
        from flask_cors import CORS

        CORS(app, resources={r"/*": {"origins": cfg.cors_origins}})
    except ImportError:
        pass

    return app


if __name__ == "__main__":
    cfg = Config.from_env()
    app = create_app(cfg)
    app.run(host=cfg.host, port=cfg.port)
