"""
Tests de SklearnPredictor.

El contrato implícito que asume esta clase es fuerte y no está escrito en ningún
lado del código:
  1. `modelo.predict_proba(df)` devuelve un array 2D con exactamente 2 columnas
     (problema binario), donde la columna 1 es P(clase positiva).
  2. `df_procesado` tiene exactamente 1 fila -- se indexa con [0] sin chequear len(df).
Estos tests separan "comportamiento correcto bajo el contrato asumido" (property-based)
de "qué pasa si el contrato se viola" (unit tests de caracterización, para dejar
documentado el modo de falla en vez de que sea una sorpresa en producción).
"""
import dataclasses

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, strategies as st, settings

from app.services.src.SklearnPredictor import SklearnPredictor


class _ModeloFake:
    """Doble de un modelo sklearn: predict_proba configurable por columnas."""

    def __init__(self, columnas):
        self._columnas = np.asarray(columnas)
        self.llamadas = []

    def predict_proba(self, df):
        self.llamadas.append(df)
        return self._columnas


def _df_una_fila():
    return pd.DataFrame([{"f1": 1.0, "f2": 2.0}])


# Property-based: bajo el contrato asumido, el resultado es correcto


@settings(max_examples=200)
@given(p=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_extrae_columna_1_como_probabilidad_de_clase_positiva(p):
    modelo = _ModeloFake([[1 - p, p]])
    predictor = SklearnPredictor(modelo=modelo)
    resultado = predictor.predecir_probabilidad(_df_una_fila())
    assert resultado == pytest.approx(p)


@settings(max_examples=100)
@given(p=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_resultado_siempre_es_float_python_nativo(p):
    """El cast explícito float(...) es parte del contrato: da igual qué dtype
    devuelva sklearn (float32, float64) -- lo que sale de acá siempre debe ser
    un float de Python, no un np.floating (importa para serializar a JSON río abajo)."""
    for dtype in (np.float32, np.float64):
        modelo = _ModeloFake(np.array([[1 - p, p]], dtype=dtype))
        predictor = SklearnPredictor(modelo=modelo)
        resultado = predictor.predecir_probabilidad(_df_una_fila())
        assert type(resultado) is float


def test_solo_usa_la_primera_fila_del_df():
    """Documenta la asunción de que df_procesado trae 1 sola fila: si por error
    llegaran más, SklearnPredictor las ignora en silencio en vez de fallar."""
    modelo = _ModeloFake([[0.9, 0.1], [0.2, 0.8], [0.5, 0.5]])
    predictor = SklearnPredictor(modelo=modelo)
    resultado = predictor.predecir_probabilidad(pd.DataFrame([{"f": 1}, {"f": 2}, {"f": 3}]))
    assert resultado == pytest.approx(0.1)  # fila 0, no la 1 ni la 2


def test_pasa_el_dataframe_completo_al_modelo_sin_transformarlo():
    df = _df_una_fila()
    modelo = _ModeloFake([[0.7, 0.3]])
    predictor = SklearnPredictor(modelo=modelo)
    predictor.predecir_probabilidad(df)
    assert modelo.llamadas[0] is df

# Caracterización: violaciones del contrato asumido

def test_predict_proba_con_una_sola_columna_lanza_indexerror():
    """Si el modelo no es un clasificador binario 'de manual' (ej. devuelve una
    sola probabilidad por fila en vez de [P(0), P(1)]), el slice [:, 1] revienta.
    No hay manejo explícito de este caso -- se documenta el modo de falla real."""
    modelo = _ModeloFake([[0.5]])
    predictor = SklearnPredictor(modelo=modelo)
    with pytest.raises(IndexError):
        predictor.predecir_probabilidad(_df_una_fila())


def test_predict_proba_con_dataframe_vacio_lanza_indexerror():
    modelo = _ModeloFake(np.empty((0, 2)))
    predictor = SklearnPredictor(modelo=modelo)
    with pytest.raises(IndexError):
        predictor.predecir_probabilidad(pd.DataFrame())


def test_predict_proba_multiclase_toma_la_columna_1_sin_avisar():
    """Con 3+ clases, predict_proba tiene 3+ columnas. El código toma la columna 1
    igual, como si fuera la probabilidad de 'default', sin validar que el modelo
    sea binario. Esto es un riesgo silencioso si algún día se reentrena con más
    de 2 clases: no hay ningún error, solo un número que ya no significa lo que
    el resto del sistema asume que significa."""
    modelo = _ModeloFake([[0.2, 0.5, 0.3]])  # 3 clases
    predictor = SklearnPredictor(modelo=modelo)
    resultado = predictor.predecir_probabilidad(_df_una_fila())
    assert resultado == pytest.approx(0.5)  # "funciona" pero es semánticamente incorrecto

# Contrato de inmutabilidad (dataclass frozen)


def test_es_inmutable():
    predictor = SklearnPredictor(modelo=_ModeloFake([[0.5, 0.5]]))
    with pytest.raises(dataclasses.FrozenInstanceError):
        predictor.modelo = _ModeloFake([[0.1, 0.9]])
