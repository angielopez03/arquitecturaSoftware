import pytest

from backend.domain.errors import ParametroInvalido, ValorFisicamenteImposible
from backend.domain.model.enums import IndicatorLevel, PlantStatus
from backend.domain.model.medicion import Medicion
from backend.domain.model.rango import Rango
from backend.domain.rules.aggregation_rule import ReglaPorDesviaciones


def test_todos_los_indicadores_optimos_son_saludables():
    niveles = {
        "humedad": IndicatorLevel.OPTIMO,
        "luz": IndicatorLevel.OPTIMO,
        "temperatura": IndicatorLevel.OPTIMO,
    }

    assert ReglaPorDesviaciones().agregar(niveles) == PlantStatus.SALUDABLE


def test_una_desviacion_deja_la_planta_en_riesgo():
    niveles = {
        "humedad": IndicatorLevel.BAJO,
        "luz": IndicatorLevel.OPTIMO,
        "temperatura": IndicatorLevel.OPTIMO,
    }

    assert ReglaPorDesviaciones().agregar(niveles) == PlantStatus.EN_RIESGO


def test_dos_desviaciones_dejan_la_planta_critica():
    niveles = {
        "humedad": IndicatorLevel.BAJO,
        "luz": IndicatorLevel.ALTO,
        "temperatura": IndicatorLevel.OPTIMO,
    }

    assert ReglaPorDesviaciones().agregar(niveles) == PlantStatus.CRITICO


def test_no_se_agrega_una_coleccion_vacia():
    with pytest.raises(ParametroInvalido):
        ReglaPorDesviaciones().agregar({})


@pytest.mark.parametrize(
    "valores",
    [
        {"humedad": 101, "luz": 10, "temperatura": 20},
        {"humedad": 50, "luz": -1, "temperatura": 20},
        {"humedad": 50, "luz": 10, "temperatura": -51},
    ],
)
def test_rechaza_limites_fisicos(valores):
    with pytest.raises(ValorFisicamenteImposible):
        Medicion(**valores)


def test_rechaza_rango_invertido():
    with pytest.raises(ValueError):
        Rango(20, 10)