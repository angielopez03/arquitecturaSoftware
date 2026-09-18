from typing import Optional
from flask import Flask

from backend.infrastructure.config import Config
from backend.infrastructure.csv_range_repository import CSVRangeRepository
from backend.domain.rules.indicator_evaluator import IndicatorEvaluator
from backend.application.diagnosis_service import DiagnosisService
from backend.application.list_species_service import ListSpeciesService
from backend.presentation.plant_controller import plant_bp


def create_app(config: Optional[Config] = None) -> Flask:
    """
    Application Factory & Composition Root (RA3).
    Único punto del sistema donde se ensamblan las implementaciones concretas
    de las cuatro capas arquitectónicas.
    """
    cfg = config or Config.from_env()
    app = Flask(__name__)

    # =========================================================================
    # --- COMPOSITION ROOT: ENSAMBLE DE LAS 4 CAPAS ---
    # =========================================================================

    # 1. INFRAESTRUCTURA (Acceso a datos y adaptadores secundarios)
    # -------------------------------------------------------------------------
    # [ESCENARIO DE EVOLUCIÓN: Migración CSV -> Base de datos relacional (PostgreSQL)]
    # Para cambiar CSV -> DB: se crea SQLRangeRepository(RangeRepository) en
    # infrastructure/ y se sustituye únicamente esta línea por:
    #   range_repository = SQLRangeRepository(connection_string=cfg.database_url)
    # Cero cambios en la capa de aplicación ni en el dominio (RA5 / DIP / LSP).
    range_repository = CSVRangeRepository(cfg.csv_path)

    # 2. DOMINIO (Entidades, Value Objects y Reglas de Negocio Puras)
    # -------------------------------------------------------------------------
    # Evaluador de indicadores individuales (SRP / OCP).
    evaluator = IndicatorEvaluator()

    # 3. APLICACIÓN (Casos de uso y orquestación agnóstica a transporte)
    # -------------------------------------------------------------------------
    # [ESCENARIO DE EVOLUCIÓN: Mediciones por MQTT desde ESP32 en vez de HTTP]
    # Para soportar MQTT: se agrega un suscriptor en infrastructure/mqtt/ que
    # recibe el mensaje del sensor, construye una Measurement de dominio y
    # llama a diagnosis_service.diagnose(especie, measurement).
    # Ni el dominio ni el caso de uso se modifican (0 líneas de cambio).
    diagnosis_service = DiagnosisService(repository=range_repository, evaluator=evaluator)

    # Caso de uso: Listar catálogo de especies soportadas y sus rangos (RF5).
    list_species_service = ListSpeciesService(repository=range_repository)

    # [ESCENARIOS DE EVOLUCIÓN FUTURA]
    # - Usuarios y múltiples plantas: nuevo contexto en domain/usuarios/ sin tocar el diagnóstico.
    # - Gamificación: servicio en la capa de aplicación que reacciona al resultado del diagnóstico.

    # 4. PRESENTACIÓN (Adaptadores primarios: REST / HTTP / Vistas)
    # -------------------------------------------------------------------------
    app.config["CONFIG"] = cfg
    app.config["DIAGNOSIS_SERVICE"] = diagnosis_service
    app.config["LIST_SPECIES_SERVICE"] = list_species_service

    app.register_blueprint(plant_bp)

    # 5. SEGURIDAD Y ORIGEN CRUZADO (RA7 / H-14)
    # -------------------------------------------------------------------------
    # Permite al front independiente (servido en otro puerto/origen) consumir la API
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
