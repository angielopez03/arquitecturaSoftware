from typing import Optional
from flask import Flask

from backend.domain.rules.indicator_evaluator import IndicatorEvaluator
from backend.application.diagnosis_service import DiagnosisService
from backend.infrastructure.csv_range_repository import CSVRangeRepository
from backend.infrastructure.config import Config
from backend.presentation.plant_controller import plant_bp


def create_app(config: Optional[Config] = None) -> Flask:
    """
    Application Factory & Composition Root.
    Ensambla las dependencias concretas en base a la configuración inyectada o de entorno.
    """
    cfg = config or Config.from_env()
    app = Flask(__name__)

    # --- Composition Root ---
    # Único lugar donde se elige la implementación concreta.
    # Cambiar CSV -> DB: reemplazar esta línea por SQLRangeRepository(...)
    range_repository = CSVRangeRepository(cfg.csv_path)

    evaluator = IndicatorEvaluator()
    diagnosis_service = DiagnosisService(repository=range_repository, evaluator=evaluator)

    app.config["CONFIG"] = cfg
    app.config["DIAGNOSIS_SERVICE"] = diagnosis_service

    app.register_blueprint(plant_bp)

    return app


if __name__ == "__main__":
    cfg = Config.from_env()
    app = create_app(cfg)
    app.run(host=cfg.host, port=cfg.port)
