"""
Tests de ShapTreeExplainer.

Dos focos, porque hay dos contratos distintos y uno de ellos es frágil:

1. Selección de top-k features por impacto absoluto (`calcular_impacto`): esto es
   puramente algorítmico y se presta bien a property-based testing sobre vectores
   de impacto arbitrarios.

2. El `match valores_shap: case [_, clase_positiva]: ... case _: ...`: esto intenta
   distinguir "lista de 2 arrays, uno por clase, típico de shap viejo en clasificación
   binaria" de "un solo array de salida". El pattern matching estructural de Python
   NO trata un `numpy.ndarray` como sequence pattern (no es instancia registrada de
   `collections.abc.Sequence`), así que el `case [_, clase_positiva]` **solo puede
   matchear si `valores_shap` es una lista/tupla de Python**, nunca un ndarray, sin
   importar su shape. Esto se verificó empíricamente (ver más abajo) y se deja
   como test de caracterización porque versiones nuevas de shap devuelven un único
   ndarray (n_clases, n_muestras, n_features) para clasificación binaria en vez de
   una lista de 2 arrays -- si eso pasara acá, el código cae siempre a la rama
   `case _`, y con un ndarray de shape (2, 1, n) eso produce un impacto de forma
   equivocada que después revienta en `pd.Series`. Este es un riesgo real de
   incompatibilidad de versión de shap, no un caso de borde inventado.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, strategies as st, settings

from app.services.ShapTreeExplainer import ShapTreeExplainer


@dataclass(frozen=True)
class _FakeShapConfig:
    cantidad_features: int


class _ExplainerFake:
    """Doble de shap.TreeExplainer: shap_values(df) devuelve lo que le pasemos."""

    def __init__(self, valores_a_devolver):
        self._valores = valores_a_devolver

    def shap_values(self, df):
        return self._valores


def _columnas(n):
    return [f"f{i}" for i in range(n)]


# ---------------------------------------------------------------------------
# Property-based: selección de top-k por impacto absoluto
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(
    impactos=st.lists(
        st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        min_size=1, max_size=15, unique=True,  # unique evita empates -> orden determinista
    ),
    k=st.integers(min_value=0, max_value=20),
)
def test_devuelve_exactamente_las_k_features_de_mayor_impacto_absoluto(impactos, k):
    columnas = _columnas(len(impactos))
    explainer = ShapTreeExplainer(
        explainer=_ExplainerFake(np.array([impactos])),
        config=_FakeShapConfig(cantidad_features=k),
    )
    resultado = explainer.calcular_impacto(pd.DataFrame([impactos], columns=columnas), columnas)

    n_esperado = min(k, len(impactos)) if k >= 0 else 0
    assert len(resultado) == n_esperado

    # invariante central: ninguna feature incluida tiene |impacto| menor que
    # ninguna feature excluida (es realmente el top-k por magnitud absoluta)
    incluidas = set(resultado.keys())
    if incluidas and len(incluidas) < len(columnas):
        min_incluido = min(abs(impactos[columnas.index(c)]) for c in incluidas)
        max_excluido = max(abs(impactos[columnas.index(c)]) for c in columnas if c not in incluidas)
        assert min_incluido >= max_excluido


@settings(max_examples=100)
@given(
    impactos=st.lists(
        st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
        min_size=1, max_size=10,
    ),
)
def test_valores_devueltos_coinciden_redondeados_a_4_decimales(impactos):
    columnas = _columnas(len(impactos))
    explainer = ShapTreeExplainer(
        explainer=_ExplainerFake(np.array([impactos])),
        config=_FakeShapConfig(cantidad_features=len(impactos)),
    )
    resultado = explainer.calcular_impacto(pd.DataFrame([impactos], columns=columnas), columnas)
    for col, valor in resultado.items():
        idx = columnas.index(col)
        assert valor == round(impactos[idx], 4)


def test_cantidad_features_cero_devuelve_diccionario_vacio():
    columnas = _columnas(5)
    explainer = ShapTreeExplainer(
        explainer=_ExplainerFake(np.array([[0.1, 0.2, 0.3, 0.4, 0.5]])),
        config=_FakeShapConfig(cantidad_features=0),
    )
    resultado = explainer.calcular_impacto(pd.DataFrame([[0.1, 0.2, 0.3, 0.4, 0.5]], columns=columnas), columnas)
    assert resultado == {}


def test_cantidad_features_mayor_a_columnas_devuelve_todas_sin_error():
    columnas = _columnas(3)
    explainer = ShapTreeExplainer(
        explainer=_ExplainerFake(np.array([[0.1, -0.9, 0.3]])),
        config=_FakeShapConfig(cantidad_features=999),
    )
    resultado = explainer.calcular_impacto(pd.DataFrame([[0.1, -0.9, 0.3]], columns=columnas), columnas)
    assert set(resultado.keys()) == set(columnas)


def test_empates_en_impacto_absoluto_desempatan_por_orden_original():
    """pandas Series.nlargest usa keep='first' por default: ante un empate en
    |impacto|, gana la columna que aparece primero en la lista original. Vale la
    pena fijar este comportamiento explícitamente porque es fácil que alguien
    cambie a keep='all' pensando que es un no-op y no lo es (puede devolver más
    de cantidad_features filas)."""
    columnas = ["a", "b", "c", "d"]
    impactos = [0.5, -0.5, 0.5, 0.1]  # "a" y "c" empatan en |impacto|=0.5 con "b"
    explainer = ShapTreeExplainer(
        explainer=_ExplainerFake(np.array([impactos])),
        config=_FakeShapConfig(cantidad_features=2),
    )
    resultado = explainer.calcular_impacto(pd.DataFrame([impactos], columns=columnas), columnas)
    assert set(resultado.keys()) == {"a", "b"}  # "a" antes que "c" por orden original


# ---------------------------------------------------------------------------
# El match/case: qué formas de valores_shap toma cada rama
# ---------------------------------------------------------------------------

def test_lista_de_dos_arrays_toma_la_segunda_como_clase_positiva():
    """Forma clásica de shap<0.45 para TreeExplainer en clasificación binaria:
    lista [array_clase_0, array_clase_1]. Debe usarse la segunda."""
    columnas = _columnas(3)
    clase_0 = np.array([[0.9, 0.9, 0.9]])
    clase_1 = np.array([[0.1, -0.2, 0.3]])
    explainer = ShapTreeExplainer(
        explainer=_ExplainerFake([clase_0, clase_1]),
        config=_FakeShapConfig(cantidad_features=3),
    )
    resultado = explainer.calcular_impacto(pd.DataFrame([[0, 0, 0]], columns=columnas), columnas)
    assert resultado == {"f2": 0.3, "f1": -0.2, "f0": 0.1}


def test_array_2d_simple_usa_la_primera_fila_directamente():
    """Forma de salida single-output (p.ej. regresión, o shap ya reducido a la
    clase positiva antes de llegar acá): un solo ndarray (n_muestras, n_features)."""
    columnas = _columnas(3)
    explainer = ShapTreeExplainer(
        explainer=_ExplainerFake(np.array([[0.1, -0.2, 0.3]])),
        config=_FakeShapConfig(cantidad_features=3),
    )
    resultado = explainer.calcular_impacto(pd.DataFrame([[0, 0, 0]], columns=columnas), columnas)
    assert resultado == {"f2": 0.3, "f1": -0.2, "f0": 0.1}


@pytest.mark.parametrize(
    "shape",
    [(2, 3), (2, 1, 3), (1, 3, 2)],
    ids=["ndarray_2_por_n", "ndarray_2_1_n_binario_nuevo", "ndarray_1_n_2_clases_al_final"],
)
def test_ningun_shape_de_ndarray_matchea_la_rama_binaria_solo_las_listas(shape):
    """CARACTERIZACIÓN DE UN RIESGO REAL: ningún ndarray -- sin importar su shape --
    hace match con `case [_, clase_positiva]`, porque numpy.ndarray no es una
    Sequence de Python a los fines del pattern matching estructural. Solo una
    `list` (o `tuple`) de longitud 2 dispara esa rama.

    Consecuencia concreta: si se actualiza la versión de `shap` y `TreeExplainer`
    empieza a devolver un único ndarray de shape (2, n_muestras, n_features) para
    clasificación binaria (comportamiento real de shap >= 0.45 en muchos casos),
    este código deja de tomar 'la clase positiva' y en su lugar cae siempre al
    `case _` (`valores_shap[0]`), tomando la primera clase o la primera muestra
    según cómo venga el array -- silenciosamente incorrecto cuando no explota,
    y con excepción cuando el resultado no es 1D (ver test siguiente)."""
    columnas = _columnas(3)
    valores = np.zeros(shape)
    explainer = ShapTreeExplainer(
        explainer=_ExplainerFake(valores),
        config=_FakeShapConfig(cantidad_features=3),
    )
    # No debe interpretarse como "clase positiva" pese a que shape[0] == 2 en
    # dos de los tres casos: siempre cae al caso default, tome forma correcta o no.
    if valores[0].ndim == 1 and valores[0].shape[0] == len(columnas):
        resultado = explainer.calcular_impacto(pd.DataFrame([[0, 0, 0]], columns=columnas), columnas)
        assert set(resultado.keys()) <= set(columnas)
    else:
        with pytest.raises(ValueError):
            explainer.calcular_impacto(pd.DataFrame([[0, 0, 0]], columns=columnas), columnas)


def test_ndarray_shape_2_1_n_binario_nuevo_rompe_con_valueerror():
    """Caso concreto y más probable en la práctica: shap >= 0.45 con TreeExplainer
    en un clasificador binario y 1 sola fila (el caso real de este servicio, que
    siempre arma un DataFrame de 1 fila) devuelve shape (2, 1, n_features).
    `valores_shap[0]` da shape (1, n_features) -- 2D -- y pd.Series revienta.
    Este test deja registrado el modo de falla exacto para que, si se actualiza
    shap, la suite avise con un traceback claro en vez de un bug silencioso en prod."""
    columnas = _columnas(3)
    valores = np.zeros((2, 1, 3))
    valores[1] = [[0.1, -0.2, 0.3]]
    explainer = ShapTreeExplainer(
        explainer=_ExplainerFake(valores),
        config=_FakeShapConfig(cantidad_features=3),
    )
    with pytest.raises(ValueError):
        explainer.calcular_impacto(pd.DataFrame([[0, 0, 0]], columns=columnas), columnas)


def test_longitud_de_impactos_distinta_a_columnas_lanza_valueerror():
    """Contrato implícito entre calcular_impacto y quien lo llama: `columnas` debe
    tener exactamente la misma longitud que el vector de impacto por fila. No hay
    validación explícita -- lo hace pd.Series por construcción."""
    columnas = _columnas(5)  # 5 nombres de columna
    explainer = ShapTreeExplainer(
        explainer=_ExplainerFake(np.array([[0.1, 0.2, 0.3]])),  # pero solo 3 impactos
        config=_FakeShapConfig(cantidad_features=3),
    )
    with pytest.raises(ValueError):
        explainer.calcular_impacto(pd.DataFrame([[0.1, 0.2, 0.3]]), columnas)
