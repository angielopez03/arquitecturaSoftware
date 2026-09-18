import os
import pytest
from backend.domain.model.entities import Measurement, Plant
from backend.domain.model.enums import IndicatorLevel, PlantStatus
from backend.domain.model.rango import Range
from backend.domain.ports.range_repository import RangeRepository
from backend.domain.rules.indicator_evaluator import IndicatorEvaluator
from backend.domain.errors import EspecieNoSoportada
from backend.application.diagnosis_service import DiagnosisService
from backend.application.list_species_service import ListSpeciesService
from backend.infrastructure.csv_range_repository import CSVRangeRepository
from backend.infrastructure.config import Config
from backend.app import create_app


# -----------------------------------------------------------------------------
# 1. PRUEBAS DEL DOMINIO (Reglas puras, sin frameworks ni I/O - RA4)
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

    # Humedad baja (10%) - 1 desviación deja la planta EN_RIESGO (RF3)
    med = Measurement(humidity=10.0, light=800.0, temperature=22.0)
    res = service.diagnose("sansevieria", med)

    assert res["status"] == PlantStatus.EN_RIESGO
    assert res["levels"]["humidity"] == IndicatorLevel.BAJO
    assert len(res["recommendations"]) >= 1
    assert "aumentar" in res["recommendations"][0].lower()


def test_diagnosis_service_two_deviations_is_critical():
    repo = FakeRangeRepository()
    service = DiagnosisService(repository=repo, evaluator=IndicatorEvaluator())

    # 2 desviaciones (humedad baja y temperatura baja) dejan la planta CRITICA (RF3)
    med = Measurement(humidity=10.0, light=800.0, temperature=5.0)
    res = service.diagnose("sansevieria", med)

    assert res["status"] == PlantStatus.CRITICO
    assert len(res["recommendations"]) >= 2


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
# 4. PRUEBAS DE INTEGRACIÓN WEB REST (RA1, RA7, RF5, RF6, Anexo A)
# -----------------------------------------------------------------------------

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_root_route_returns_pure_json(client):
    """Verifica RA1: el backend responde exclusivamente con JSON, no HTML."""
    res = client.get("/")
    assert res.status_code == 200
    assert res.is_json
    data = res.get_json()
    assert "endpoints" in data


def test_api_get_especies_catalog(client):
    """Verifica RF5: GET /api/v1/especies devuelve el catálogo en JSON."""
    res = client.get("/api/v1/especies")
    assert res.status_code == 200
    assert res.is_json
    especies = res.get_json()
    assert len(especies) >= 6
    assert any(e["nombre"] == "sansevieria" for e in especies)


def test_api_post_diagnostico_successful(client):
    """Verifica RF1-RF4: POST /api/v1/diagnosticos responde diagnóstico con Anexo A."""
    payload = {
        "especie": "sansevieria",
        "humedad": 30.0,
        "luz": 800.0,
        "temperatura": 22.0,
    }
    res = client.post("/api/v1/diagnosticos", json=payload)
    assert res.status_code == 200
    assert res.is_json
    datos = res.get_json()
    assert datos["especie"] == "sansevieria"
    assert datos["estado"] == "SALUDABLE"
    assert len(datos["parametros"]) == 3


def test_api_post_diagnostico_unknown_species_404(client):
    """Verifica RF6: Especie desconocida responde 404 con JSON uniforme."""
    payload = {
        "especie": "planta_extraterrestre",
        "humedad": 30.0,
        "luz": 800.0,
        "temperatura": 22.0,
    }
    res = client.post("/api/v1/diagnosticos", json=payload)
    assert res.status_code == 404
    assert res.is_json
    datos = res.get_json()
    assert datos["error"] == "ESPECIE_NO_SOPORTADA"
    assert "detalle" in datos


def test_api_post_diagnostico_impossible_value_400(client):
    """Verifica RF6: Valor físicamente imposible responde 400 con JSON uniforme."""
    payload = {
        "especie": "sansevieria",
        "humedad": 150.0,  # Imposible > 100%
        "luz": 800.0,
        "temperatura": 22.0,
    }
    res = client.post("/api/v1/diagnosticos", json=payload)
    assert res.status_code == 400
    assert res.is_json
    datos = res.get_json()
    assert datos["error"] == "PARAMETRO_INVALIDO"


def test_cors_headers_present(client):
    """Verifica RA7: CORS habilitado en las rutas del API."""
    res = client.get("/api/v1/especies", headers={"Origin": "http://localhost:8080"})
    assert res.status_code == 200
    assert res.headers.get("Access-Control-Allow-Origin") in ("*", "http://localhost:8080")
