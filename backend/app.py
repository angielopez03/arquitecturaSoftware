from typing import Optional

from flask import Flask

from backend.application.diagnosis_service import DiagnosisService
from backend.application.list_species_service import ListSpeciesService
from backend.domain.rules.indicator_evaluator import IndicatorEvaluator
from backend.infrastructure.config import Config
from backend.infrastructure.csv_range_repository import CSVRangeRepository
from backend.presentation.plant_controller import plant_bp


def create_app(config: Optional[Config] = None) -> Flask:
    """
    Application Factory & Composition Root (RA3).
    Único punto del sistema donde se ensamblan las implementaciones concretas
    de las cuatro capas arquitectónicas.
    """
    cfg = config or Config.from_env()
    app = Flask(__name__)

    range_repository = CSVRangeRepository(cfg.csv_path)
    evaluator = IndicatorEvaluator()
    diagnosis_service = DiagnosisService(repository=range_repository, evaluator=evaluator)
    list_species_service = ListSpeciesService(repository=range_repository)

    app.config["CONFIG"] = cfg
    app.config["DIAGNOSIS_SERVICE"] = diagnosis_service
    app.config["LIST_SPECIES_SERVICE"] = list_species_service

    app.register_blueprint(plant_bp)

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
