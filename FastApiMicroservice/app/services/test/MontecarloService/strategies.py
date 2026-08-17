from hypothesis import strategies as st
import numpy as np

from .datos import ParMonotonico, PortfolioEscenario


ESCENARIOS_TEST = 500
ESCENARIOS_PRODUCCION = 10_000

PROBABILIDAD = st.floats(
    min_value=0.0,
    max_value=1.0,
    allow_nan=False,
    allow_infinity=False,
)


def probabilidades(min_size: int = 1, max_size: int = 50):
    return st.lists(
        PROBABILIDAD,
        min_size=min_size,
        max_size=max_size,
    )


@st.composite
def portfolio_escenario(
    draw,
    min_prestamos: int = 1,
    max_prestamos: int = 50,
    escenarios: int = ESCENARIOS_TEST,
):
    return PortfolioEscenario(
        probabilidades=draw(
            probabilidades(min_prestamos, max_prestamos)
        ),
        escenarios=escenarios,
    )


@st.composite
def par_monotonico(
    draw,
    min_prestamos: int = 1,
    max_prestamos: int = 20,
    escenarios: int = ESCENARIOS_TEST,
):
    n = draw(
        st.integers(
            min_value=min_prestamos,
            max_value=max_prestamos,
        )
    )

    delta = draw(
        st.floats(
            min_value=0.0,
            max_value=1.0,
            allow_nan=False,
            allow_infinity=False,
        )
    )

    p_bajo = draw(
        st.lists(
            st.floats(
                min_value=0.0,
                max_value=1.0 - delta,
                allow_nan=False,
                allow_infinity=False,
            ),
            min_size=n,
            max_size=n,
        )
    )

    p_alto = [p + delta for p in p_bajo]

    matriz_seed = draw(
        st.integers(
            min_value=0,
            max_value=10**6,
        )
    )

    matriz_random = np.random.default_rng(matriz_seed).random(
        (escenarios, n)
    )

    return ParMonotonico(
        matriz_random=matriz_random,
        p_bajo=p_bajo,
        p_alto=p_alto,
    )