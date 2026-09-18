import pytest

from backend.domain.model.enums import IndicatorLevel
from backend.domain.model.rango import Rango
from backend.domain.ports.range_repository import ProveedorRangos
from backend.domain.rules.indicator_evaluator import IndicatorEvaluator


class ProveedorRangosFalso(ProveedorRangos):
    def obtener_rangos(self, especie: str):
        return {
            "humedad": Rango(40, 70),
            "ph": Rango(6, 7),
        }


@pytest.fixture
def evaluador():
    return IndicatorEvaluator()


def test_doble_de_proveedor_entrega_rangos():
    rangos = ProveedorRangosFalso().obtener_rangos("tomate")

    assert set(rangos) == {"humedad", "ph"}
    assert rangos["ph"] == Rango(6, 7)


def test_clasifica_carencia_como_bajo(evaluador):
    assert evaluador.evaluate(39, Rango(40, 70)) == IndicatorLevel.BAJO


def test_clasifica_valor_en_rango_como_optimo(evaluador):
    assert evaluador.evaluate(55, Rango(40, 70)) == IndicatorLevel.OPTIMO


def test_clasifica_exceso_como_alto(evaluador):
    assert evaluador.evaluate(71, Rango(40, 70)) == IndicatorLevel.ALTO


def test_clasifica_coleccion_con_ph(evaluador):
    niveles = evaluador.evaluate_collection(
        values={"humedad": 55, "ph": 7.5},
        optimal_ranges=ProveedorRangosFalso().obtener_rangos("tomate"),
    )

    assert niveles == {
        "humedad": IndicatorLevel.OPTIMO,
        "ph": IndicatorLevel.ALTO,
    }