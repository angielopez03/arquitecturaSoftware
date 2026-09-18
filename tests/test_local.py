import os
import pytest
from backend.domain.models.entities import Measurement, Plant
from backend.domain.models.enums import IndicatorLevel, PlantStatus
from backend.domain.models.value_objects import Range
from backend.domain.ports.range_repository import RangeRepository
from backend.domain.rules.indicator_evaluator import IndicatorEvaluator
from backend.domain.errors import EspecieNoSoportada
from backend.application.diagnosis_service import DiagnosisService
from backend.application.list_species_service import ListSpeciesService
from backend.infrastructure.csv_range_repository import CSVRangeRepository
from backend.infrastructure.config import Config
from backend.app import create_app


# -----------------------------------------------------------------------------
# 1. PRUEBAS DEL DOMINIO (Reglas puras, sin frameworks ni I/O)
# -----------------------------------------------------------------------------

def test_range_contains_and_distance():
    r = Range(20.0, 50.0)
    assert r.contains(30.0)
    assert not r.contains(10.0)
    assert not r.contains(60.0)


def test_indicator_evaluator_distinguishes_deficiency_and_excess():
    """Verifica RF2 y solución a H-05: distingue BAJO de ALTO."""
    evaluator = IndicatorEvaluator()
    r = Range(40.0, 70.0)

    assert evaluator.evaluate(55.0, r) == IndicatorLevel.OPTIMO
    assert evaluator.evaluate(20.0, r) == IndicatorLevel.BAJO
    assert evaluator.evaluate(85.0, r) == IndicatorLevel.ALTO


def test_domain_exceptions():
    """Verifica jerarquía de excepciones de dominio (H-06 / RF6)."""
    err = EspecieNoSoportada("bonsai_marciano")
    assert err.especie == "bonsai_marciano"
    assert "no está soportada" in str(err)


# -----------------------------------------------------------------------------
# 2. PRUEBAS DE APLICACIÓN CON DOBLES (RA4 / RA5 / LSP)
# -----------------------------------------------------------------------------

class FakeRangeRepository(RangeRepository):
    """Doble de prueba para verificar que la aplicación funciona sin CSV ni BD."""
    def get_ranges(self, plant_type: str):
        if plant_type != "sansevieria":
            raise EspecieNoSoportada(plant_type)
        return {
            "humidity": Range(20.0, 45.0),
            "light": Range(200.0, 1500.0),
            "temperature": Range(15.0, 29.0),
        }

    def get_all_species(self):
        return {
            "sansevieria": {
                "humidity": Range(20.0, 45.0),
                "light": Range(200.0, 1500.0),
                "temperature": Range(15.0, 29.0),
            }
        }


def test_diagnosis_service_all_optimal():
    repo = FakeRangeRepository()
    service = DiagnosisService(repository=repo, evaluator=IndicatorEvaluator())

    # Lectura óptima
    med = Measurement(humidity=30.0, light=800.0, temperature=22.0)
    res = service.diagnose("sansevieria", med)

    assert res["status"] == PlantStatus.SALUDABLE
    assert len(res["recommendations"]) == 0
    assert res["levels"]["humidity"] == IndicatorLevel.OPTIMO


def test_diagnosis_service_deficiency_recommends_increase():
    repo = FakeRangeRepository()
    service = DiagnosisService(repository=repo, evaluator=IndicatorEvaluator())

    # Humedad baja (10%)
    med = Measurement(humidity=10.0, light=800.0, temperature=22.0)
    res = service.diagnose("sansevieria", med)

    assert res["status"] == PlantStatus.CRITICO
    assert res["levels"]["humidity"] == IndicatorLevel.BAJO
    assert len(res["recommendations"]) >= 1
    assert "aumentar" in res["recommendations"][0].lower()


def test_diagnosis_service_excess_recommends_decrease():
    repo = FakeRangeRepository()
    service = DiagnosisService(repository=repo, evaluator=IndicatorEvaluator())

    # Humedad alta (80%)
    med = Measurement(humidity=80.0, light=800.0, temperature=22.0)
    res = service.diagnose("sansevieria", med)

    assert res["status"] == PlantStatus.EN_RIESGO
    assert res["levels"]["humidity"] == IndicatorLevel.ALTO
    assert len(res["recommendations"]) >= 1
    assert "reducir" in res["recommendations"][0].lower()


def test_diagnosis_service_unknown_species_raises_domain_error():
    repo = FakeRangeRepository()
    service = DiagnosisService(repository=repo, evaluator=IndicatorEvaluator())
    med = Measurement(humidity=30.0, light=800.0, temperature=22.0)

    with pytest.raises(EspecieNoSoportada) as exc_info:
        service.diagnose("alien_plant", med)
    assert exc_info.value.especie == "alien_plant"


def test_list_species_service_catalog():
    repo = FakeRangeRepository()
    service = ListSpeciesService(repository=repo)
    catalogo = service.execute()

    assert len(catalogo) == 1
    assert catalogo[0]["nombre"] == "sansevieria"
    assert "rangos" in catalogo[0]


# -----------------------------------------------------------------------------
# 3. PRUEBAS DE INFRAESTRUCTURA (CSV, Config, Fuentes)
# -----------------------------------------------------------------------------

def test_config_from_env_defaults():
    cfg = Config.from_env()
    assert os.path.exists(cfg.csv_path)
    assert cfg.port == 5000
    assert cfg.host == "0.0.0.0"
    assert cfg.cors_origins == "*"


def test_csv_repository_loads_real_data_with_lux():
    """Verifica H-11: 6+ especies reales, sin default, con luz en lux."""
    cfg = Config.from_env()
    repo = CSVRangeRepository(cfg.csv_path)
    species = repo.get_all_species()

    # Mínimo 5 especies
    assert len(species) >= 6, f"Se esperaban al menos 6 especies, hay {len(species)}"
    assert "default" not in species

    # Comprobar que las unidades de luz son de orden lux (> 100)
    for name, ranges in species.items():
        assert ranges["light"].max_value >= 500, f"Luz de {name} no parece estar en lux"


def test_csv_repository_unknown_species_raises_error():
    """Verifica H-06: especie desconocida no devuelve diagnóstico inventado."""
    cfg = Config.from_env()
    repo = CSVRangeRepository(cfg.csv_path)

    with pytest.raises(EspecieNoSoportada):
        repo.get_ranges("bonsai_marciano")


# -----------------------------------------------------------------------------
# 4. PRUEBAS DE INTEGRACIÓN WEB (Flask, CORS, Vistas)
# -----------------------------------------------------------------------------

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    res = client.get("/")
    assert res.status_code == 200


def test_evaluar_route_returns_result(client):
    data = {
        "plant_name": "Mi Helecho",
        "plant_type": "helecho",
        "humidity": "70",
        "light": "400",
        "temperature": "20",
    }
    res = client.post("/evaluar", data=data)
    assert res.status_code == 200
    assert b"SALUDABLE" in res.data or b"Diagn" in res.data


def test_cors_headers_present(client):
    """Verifica RA7: CORS habilitado."""
    res = client.get("/", headers={"Origin": "http://localhost:8080"})
    assert res.status_code == 200
    # Flask-CORS añade Access-Control-Allow-Origin
    assert res.headers.get("Access-Control-Allow-Origin") in ("*", "http://localhost:8080")
