"""
Tests de ScoringService.predecir.

Acá el foco no es el algoritmo (eso ya lo cubren los tests de cada colaborador),
sino el CONTRATO DE ORQUESTACIÓN:
  - qué recibe cada colaborador y en qué orden se llaman
  - qué pasa cuando cualquiera de los 4 colaboradores falla (deben envolverse
    SIEMPRE en RuntimeError, preservando la excepción original como __cause__,
    sin importar cuál de los 4 fue el que rompió)
  - que la salida se arma con CreditRiskResponse.armar_respuesta con los nombres
    de argumento correctos

predictor / clasificador / explainer están definidos como Protocol en interfaces.py,
así que se testean con dobles (Mock/fakes) sin ninguna dependencia de sklearn o shap
reales -- es exactamente lo que la inyección de dependencias de este servicio permite,
y es lo que lo hace testeable sin levantar el modelo real.

CreditRiskResponse SÍ está importada y usada directamente (no inyectada) dentro de
ScoringService, así que para aislar la orquestación se la mockea vía monkeypatch en
el propio módulo `app.services.ScoringService`, sin depender de su implementación real.
"""
from unittest.mock import MagicMock

import pandas as pd
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

import app.services.ScoringService as scoring_service_module
from app.services.ScoringService import ScoringService


class _FakePreprocesador:
    def __init__(self, transformar=None):
        self.llamadas = []
        self._transformar = transformar or (lambda df: df)

    def transformar(self, df):
        self.llamadas.append(df)
        return self._transformar(df)


def _service(preprocesador=None, predictor=None, clasificador=None, explainer=None, columnas=None):
    return ScoringService(
        preprocesador=preprocesador or _FakePreprocesador(),
        predictor=predictor or MagicMock(predecir_probabilidad=MagicMock(return_value=0.42)),
        clasificador=clasificador or MagicMock(decision_binaria=MagicMock(return_value=1),
                                                clasificar_riesgo=MagicMock(return_value="ALTA")),
        explainer=explainer or MagicMock(calcular_impacto=MagicMock(return_value={"f1": 0.1})),
        columnas_entrenamiento=columnas if columnas is not None else ["f1", "f2"],
    )


@pytest.fixture
def credit_risk_response_mock(monkeypatch):
    """Reemplaza CreditRiskResponse dentro del módulo bajo test por un doble que
    solo registra con qué kwargs fue llamado -- sin acoplarse a su implementación real."""
    fake_cls = MagicMock()
    fake_cls.armar_respuesta = MagicMock(side_effect=lambda **kwargs: kwargs)
    monkeypatch.setattr(scoring_service_module, "CreditRiskResponse", fake_cls)
    return fake_cls


# ---------------------------------------------------------------------------
# Orquestación: quién recibe qué, y en qué orden
# ---------------------------------------------------------------------------

def test_arma_un_dataframe_de_una_fila_a_partir_del_payload(credit_risk_response_mock):
    preproc = _FakePreprocesador()
    service = _service(preprocesador=preproc)
    service.predecir({"edad": 30, "ingreso": 50000})

    df_recibido = preproc.llamadas[0]
    assert isinstance(df_recibido, pd.DataFrame)
    assert len(df_recibido) == 1
    assert list(df_recibido.columns) == ["edad", "ingreso"]
    assert df_recibido.iloc[0]["edad"] == 30


def test_el_predictor_recibe_el_dataframe_ya_procesado_no_el_crudo(credit_risk_response_mock):
    marcador_procesado = pd.DataFrame([{"procesado": True}])
    preproc = _FakePreprocesador(transformar=lambda df: marcador_procesado)
    predictor = MagicMock(predecir_probabilidad=MagicMock(return_value=0.5))
    service = _service(preprocesador=preproc, predictor=predictor)

    service.predecir({"edad": 30})

    df_pasado_al_predictor = predictor.predecir_probabilidad.call_args[0][0]
    assert df_pasado_al_predictor is marcador_procesado


def test_el_explainer_recibe_columnas_entrenamiento_sin_modificar(credit_risk_response_mock):
    explainer = MagicMock(calcular_impacto=MagicMock(return_value={}))
    columnas = ["f1", "f2", "f3"]
    service = _service(explainer=explainer, columnas=columnas)

    service.predecir({"f1": 1, "f2": 2, "f3": 3})

    _, columnas_pasadas = explainer.calcular_impacto.call_args[0]
    assert columnas_pasadas == columnas
    assert columnas_pasadas is columnas  # no se copia ni se reconstruye


def test_orden_de_llamadas_es_transformar_predecir_clasificar_explicar(credit_risk_response_mock):
    orden = []
    preproc = MagicMock()
    preproc.transformar = MagicMock(side_effect=lambda df: (orden.append("transformar"), df)[1])
    predictor = MagicMock()
    predictor.predecir_probabilidad = MagicMock(side_effect=lambda df: (orden.append("predecir"), 0.5)[1])
    clasificador = MagicMock()
    clasificador.decision_binaria = MagicMock(side_effect=lambda p: (orden.append("decision"), 1)[1])
    clasificador.clasificar_riesgo = MagicMock(side_effect=lambda p: (orden.append("clasificar"), "ALTA")[1])
    explainer = MagicMock()
    explainer.calcular_impacto = MagicMock(side_effect=lambda df, c: (orden.append("explicar"), {})[1])

    service = _service(preprocesador=preproc, predictor=predictor, clasificador=clasificador, explainer=explainer)
    service.predecir({"f1": 1})

    assert orden == ["transformar", "predecir", "decision", "clasificar", "explicar"]


def test_arma_la_respuesta_con_los_kwargs_correctos(credit_risk_response_mock):
    predictor = MagicMock(predecir_probabilidad=MagicMock(return_value=0.73))
    clasificador = MagicMock(decision_binaria=MagicMock(return_value=1), clasificar_riesgo=MagicMock(return_value="ALTA"))
    explainer = MagicMock(calcular_impacto=MagicMock(return_value={"f1": 0.2}))
    service = _service(predictor=predictor, clasificador=clasificador, explainer=explainer)

    resultado = service.predecir({"f1": 1})

    credit_risk_response_mock.armar_respuesta.assert_called_once_with(
        probabilidad_default=0.73,
        etiqueta="ALTA",
        prediccion_default=1,
        explicacion={"f1": 0.2},
    )
    assert resultado == {
        "probabilidad_default": 0.73,
        "etiqueta": "ALTA",
        "prediccion_default": 1,
        "explicacion": {"f1": 0.2},
    }


# ---------------------------------------------------------------------------
# Manejo de errores: cualquier falla de cualquier colaborador -> RuntimeError
# ---------------------------------------------------------------------------

class _ErrorDePrueba(Exception):
    pass


@pytest.mark.parametrize("colaborador_que_falla", ["preprocesador", "predictor", "clasificador_decision",
                                                     "clasificador_etiqueta", "explainer"])
def test_error_de_cualquier_colaborador_se_envuelve_en_runtimeerror(colaborador_que_falla, credit_risk_response_mock):
    kwargs = {}
    if colaborador_que_falla == "preprocesador":
        kwargs["preprocesador"] = MagicMock(transformar=MagicMock(side_effect=_ErrorDePrueba("boom")))
    elif colaborador_que_falla == "predictor":
        kwargs["predictor"] = MagicMock(predecir_probabilidad=MagicMock(side_effect=_ErrorDePrueba("boom")))
    elif colaborador_que_falla == "clasificador_decision":
        kwargs["clasificador"] = MagicMock(decision_binaria=MagicMock(side_effect=_ErrorDePrueba("boom")))
    elif colaborador_que_falla == "clasificador_etiqueta":
        clf = MagicMock(decision_binaria=MagicMock(return_value=1))
        clf.clasificar_riesgo = MagicMock(side_effect=_ErrorDePrueba("boom"))
        kwargs["clasificador"] = clf
    elif colaborador_que_falla == "explainer":
        kwargs["explainer"] = MagicMock(calcular_impacto=MagicMock(side_effect=_ErrorDePrueba("boom")))

    service = _service(**kwargs)

    with pytest.raises(RuntimeError) as exc_info:
        service.predecir({"f1": 1})

    assert "Error procesando el modelo" in str(exc_info.value)
    # la excepción original no se pierde -- queda encadenada para debugging/logging
    assert isinstance(exc_info.value.__cause__, _ErrorDePrueba)


def test_si_arma_respuesta_falla_no_se_envuelve_en_runtimeerror(credit_risk_response_mock):
    """El try/except de ScoringService.predecir cubre los pasos 1 a 4 (transformar,
    predecir, reglas de negocio, explicar) pero NO el armado final de la respuesta,
    que queda fuera del bloque try. Si armar_respuesta explota, la excepción sale
    tal cual -- no como RuntimeError. Documentado porque es asimétrico respecto a
    los otros 4 pasos y podría no ser intencional."""
    credit_risk_response_mock.armar_respuesta.side_effect = _ErrorDePrueba("boom en el armado")
    service = _service()
    with pytest.raises(_ErrorDePrueba):
        service.predecir({"f1": 1})


# ---------------------------------------------------------------------------
# Property-based sobre la forma del payload de entrada
# ---------------------------------------------------------------------------

_valor_payload = st.one_of(
    st.integers(min_value=-10_000, max_value=10_000),
    st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6),
    st.text(max_size=20),
    st.booleans(),
    st.none(),
)


@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(payload=st.dictionaries(st.text(min_size=1, max_size=15).filter(str.isidentifier), _valor_payload, min_size=0, max_size=8))
def test_cualquier_payload_dict_se_convierte_en_dataframe_de_una_fila(payload, credit_risk_response_mock):
    preproc = _FakePreprocesador()
    service = _service(preprocesador=preproc)

    service.predecir(payload)

    df = preproc.llamadas[-1]
    assert len(df) == 1
    assert set(df.columns) == set(payload.keys())
