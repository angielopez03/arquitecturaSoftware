import os
from flask import Flask

from backend.domain.rules.indicator_evaluator import IndicatorEvaluator
from backend.application.diagnosis_service import DiagnosisService
from backend.infrastructure.csv_range_repository import CSVRangeRepository
from backend.infrastructure.input_provider import ManualInputProvider
from backend.presentation.plant_controller import plant_bp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "plant_ranges.csv")


def create_app() -> Flask:
    app = Flask(__name__)

    # --- Composition Root ---
    # Único lugar donde se elige la implementación concreta.
    # Cambiar CSV -> DB: reemplazar esta línea por SQLRangeRepository(...)
    range_repository = CSVRangeRepository(CSV_PATH)

    # Cambiar manual -> sensor: reemplazar esta línea por SensorInputProvider(...)
    input_provider = ManualInputProvider()

    evaluator = IndicatorEvaluator()
    diagnosis_service = DiagnosisService(repository=range_repository, evaluator=evaluator)

    app.config["INPUT_PROVIDER"] = input_provider
    app.config["DIAGNOSIS_SERVICE"] = diagnosis_service

    app.register_blueprint(plant_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
