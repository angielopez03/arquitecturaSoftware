import os
from flask import Flask

from services.indicator_evaluator import IndicatorEvaluator
from services.diagnosis_service import DiagnosisService
from repositories.csv_range_repository import CSVRangeRepository
from repositories.input_provider import ManualInputProvider
from controllers.plant_controller import plant_bp

BACKEND_DIR = os.path.dirname(os.path.abspath(_file_))
REPO_ROOT = os.path.dirname(BACKEND_DIR)
CSV_PATH = os.path.join(REPO_ROOT, "data", "plant_ranges.csv")


def create_app() -> Flask:
    app = Flask(__name__)

    # --- Composition Root ---
    # Unico lugar donde se elige la implementacion concreta.
    # Cambiar CSV -> DB: reemplazar esta linea por SQLRangeRepository(...)
    range_repository = CSVRangeRepository(CSV_PATH)

    # Cambiar manual -> sensor: reemplazar esta linea por SensorInputProvider(...)
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
