import numpy as np

from app.domain.services import MontecarloService


def test_todas_probabilidades_cero_nunca_da_default():
    resp = MontecarloService(
        rng=np.random.default_rng(1)
    ).simular_riesgo_portfolio(
        [0.0] * 10,
        200,
    )

    assert resp.var_95 == 0
    assert resp.cvar_95 == 0


def test_todas_probabilidades_uno_siempre_da_default_total():
    resp = MontecarloService(
        rng=np.random.default_rng(1)
    ).simular_riesgo_portfolio(
        [1.0] * 10,
        200,
    )

    assert resp.var_95 == 10
    assert resp.cvar_95 == 10


def test_una_sola_simulacion_var_y_cvar_coinciden():
    resp = MontecarloService(
        rng=np.random.default_rng(1)
    ).simular_riesgo_portfolio(
        [0.3, 0.7],
        1,
    )

    assert resp.var_95 == resp.cvar_95


def test_portfolio_vacio_da_riesgo_cero():
    """
    Un portfolio vacío es un estado legítimo:
    no hay defaults posibles y el riesgo es cero.
    """
    resp = MontecarloService(
        rng=np.random.default_rng(1)
    ).simular_riesgo_portfolio(
        [],
        100,
    )

    assert resp.var_95 == 0
    assert resp.cvar_95 == 0


def test_un_solo_prestamo():
    resp = MontecarloService(
        rng=np.random.default_rng(1)
    ).simular_riesgo_portfolio(
        [0.5],
        500,
    )

    assert 0 <= resp.var_95 <= 1
    assert 0 <= resp.cvar_95 <= 1