import pytest
import pandas as pd 
from hypothesis import given, settings, HealthCheck
from app.validador import Validador
from factory_clientes import REGLAS
from tests.estrategias import df_valido, df_invalido, df_con_indice, df_mixto, df_lista_mixta
#defino el escenario
@pytest.fixture
def validador():
    return Validador({"fields": REGLAS})

#si no hay clientes el resultado no es valido (testeo contra valueError)
@given(df=df_invalido())
@settings(max_examples=10,
          suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_filtrado_unico_invalido_falla(validador, df):
    with pytest.raises(ValueError):
        validador.validar(df)

#test de idempotencia: verifico que el validador no transforma los datos. Matematicamente: f(f(x)) == f(x)
@given(df=df_valido())
@settings(max_examples=10,
          suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_idempotencia(validador, df):
    res1 = validador.validar(df)
    res2 = validador.validar(res1)
    pd.testing.assert_frame_equal(res1, res2)

#invariante de determinismo: mismo input, mismo output
@given(df=df_valido())
@settings(max_examples=10,
          suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_determinismo(validador, df):
    res1 = validador.validar(df)
    res2 = validador.validar(df)
    pd.testing.assert_frame_equal(res1, res2)
#sobrevive al filtro unicamente el cliente valido
@given(df=df_mixto())
@settings(max_examples=50,
          suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_supervivencia_valido(validador, df):
    res = validador.validar(df)
    assert res.index.tolist() == ["indice_valido"]

#invariante: cuando aplico el validador quedan unicamente los validos
@given(df=df_lista_mixta())
@settings(max_examples=100,
          suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_todos_i(validador, df):
    res = validador.validar(df)
    indices_validos = {idx for idx in df.index if idx.startswith("valido_")}
    assert set(res.index) == indices_validos