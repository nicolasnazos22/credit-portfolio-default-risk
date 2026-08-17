import numpy as np
from hypothesis import given, settings

from app.domain.services import MontecarloService

from .fakes import FakeRng
from .strategies import par_monotonico, portfolio_escenario


@settings(max_examples=30, deadline=None)
@given(portfolio_escenario())
def test_resultado_respeta_bounds_y_cantidad_de_simulaciones(caso):
    resp = MontecarloService(
        rng=np.random.default_rng(42)
    ).simular_riesgo_portfolio(
        caso.probabilidades,
        caso.escenarios,
    )

    cantidad_prestamos = len(caso.probabilidades)

    assert 0 <= resp.var_95 <= cantidad_prestamos
    assert 0 <= resp.cvar_95 <= cantidad_prestamos
    assert resp.simulaciones == caso.escenarios


@settings(max_examples=30, deadline=None)
@given(portfolio_escenario())
def test_cvar_es_mayor_o_igual_que_var(caso):
    resp = MontecarloService(
        rng=np.random.default_rng(7)
    ).simular_riesgo_portfolio(
        caso.probabilidades,
        caso.escenarios,
    )

    assert resp.cvar_95 >= resp.var_95


@settings(max_examples=30, deadline=None)
@given(par_monotonico())
def test_aumentar_probabilidades_no_reduce_el_riesgo(caso):
    # Misma realización aleatoria: solamente cambian las probabilidades.
    resp_bajo = MontecarloService(
        rng=FakeRng(caso.matriz_random)
    ).simular_riesgo_portfolio(
        caso.p_bajo,
        caso.escenarios,
    )

    resp_alto = MontecarloService(
        rng=FakeRng(caso.matriz_random)
    ).simular_riesgo_portfolio(
        caso.p_alto,
        caso.escenarios,
    )

    assert resp_alto.var_95 >= resp_bajo.var_95
    assert resp_alto.cvar_95 >= resp_bajo.cvar_95


def test_reproducibilidad():
    probabilidades = [0.1, 0.3, 0.7]
    escenarios = 500
    seed = 42

    r1 = MontecarloService(
        rng=np.random.default_rng(seed)
    ).simular_riesgo_portfolio(
        probabilidades,
        escenarios,
    )

    r2 = MontecarloService(
        rng=np.random.default_rng(seed)
    ).simular_riesgo_portfolio(
        probabilidades,
        escenarios,
    )

    assert (r1.var_95, r1.cvar_95) == (
        r2.var_95,
        r2.cvar_95,
    )


def test_acepta_cantidad_de_escenarios_de_produccion():
    probabilidades = [0.1, 0.3, 0.7]

    resp = MontecarloService(
        rng=np.random.default_rng(42)
    ).simular_riesgo_portfolio(
        probabilidades,
        10_000,
    )

    assert resp.simulaciones == 10_000