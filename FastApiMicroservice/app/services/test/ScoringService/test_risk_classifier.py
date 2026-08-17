"""
Tests de RiskClassifier: unitarios de borde + property-based (invariantes de contrato).

RiskClassifier es un dataclass frozen que solo accede a `self.configuracion.umbral_*`
por atributo (duck typing) -- no valida `isinstance(configuracion, RiskConfig)` en
runtime, ni valida que los umbrales tengan sentido entre sí. Por eso estos tests usan
un doble liviano (_FakeRiskConfig) en vez de la RiskConfig real: así se ejercita el
contrato real del clasificador sin acoplarse a cómo se construye RiskConfig en el
proyecto (no fue provista). Si RiskConfig termina validando sus campos en
__post_init__, reemplazar el doble por la clase real en los tests que generan
configuraciones inválidas a propósito.
"""
import math
from dataclasses import dataclass

from hypothesis import given, assume, strategies as st, settings

from app.services.Risk_classifier import RiskClassifier
from app.domain.schemas import EtiquetaRiesgo


@dataclass(frozen=True)
class _FakeRiskConfig:
    umbral_decision: float
    umbral_bajo: float
    umbral_medio: float


_RANK = {EtiquetaRiesgo.BAJA: 0, EtiquetaRiesgo.MEDIA: 1, EtiquetaRiesgo.ALTA: 2}

_finito = dict(allow_nan=False, allow_infinity=False)
_probas = st.floats(min_value=0.0, max_value=1.0, **_finito)
_umbrales = st.floats(min_value=0.0, max_value=1.0, **_finito)
# floats sin acotar a [0,1]: proba y umbral son *conceptualmente* probabilidades,
# pero nada en el código las fuerza a estarlo -- vale la pena probar el contrato
# también fuera de ese rango.
_floats_libres = st.floats(min_value=-1e6, max_value=1e6, **_finito)


# ---------------------------------------------------------------------------
# Unit tests: comportamiento exacto en los bordes de cada umbral
# ---------------------------------------------------------------------------

class TestDecisionBinariaBordes:
    def _clf(self, umbral_decision=0.5):
        return RiskClassifier(_FakeRiskConfig(umbral_decision=umbral_decision, umbral_bajo=0.3, umbral_medio=0.7))

    def test_igual_al_umbral_decide_riesgo_positivo(self):
        # el operador es >=: el propio umbral cae del lado "riesgoso"
        assert self._clf().decision_binaria(0.5) == 1

    def test_justo_debajo_del_umbral_decide_riesgo_negativo(self):
        justo_debajo = math.nextafter(0.5, -math.inf)
        assert self._clf().decision_binaria(justo_debajo) == 0

    def test_extremos_0_y_1(self):
        clf = self._clf()
        assert clf.decision_binaria(0.0) == 0
        assert clf.decision_binaria(1.0) == 1

    def test_umbral_en_los_extremos(self):
        # umbral_decision=0.0 -> todo (incluso proba=0.0) es riesgo positivo
        assert self._clf(umbral_decision=0.0).decision_binaria(0.0) == 1
        # umbral_decision=1.0 -> solo proba=1.0 exacto es riesgo positivo
        siempre_negativo = self._clf(umbral_decision=1.0)
        assert siempre_negativo.decision_binaria(0.999999) == 0
        assert siempre_negativo.decision_binaria(1.0) == 1


class TestClasificarRiesgoBordes:
    def setup_method(self):
        self.clf = RiskClassifier(_FakeRiskConfig(umbral_decision=0.5, umbral_bajo=0.3, umbral_medio=0.7))

    def test_igual_a_umbral_bajo_es_baja(self):
        # proba <= umbral_bajo -> BAJA (borde inclusivo hacia abajo)
        assert self.clf.clasificar_riesgo(0.3) == EtiquetaRiesgo.BAJA

    def test_justo_encima_de_umbral_bajo_es_media(self):
        justo_encima = math.nextafter(0.3, math.inf)
        assert self.clf.clasificar_riesgo(justo_encima) == EtiquetaRiesgo.MEDIA

    def test_igual_a_umbral_medio_es_media(self):
        # umbral_bajo < proba <= umbral_medio -> MEDIA (borde inclusivo hacia arriba)
        assert self.clf.clasificar_riesgo(0.7) == EtiquetaRiesgo.MEDIA

    def test_justo_encima_de_umbral_medio_es_alta(self):
        justo_encima = math.nextafter(0.7, math.inf)
        assert self.clf.clasificar_riesgo(justo_encima) == EtiquetaRiesgo.ALTA

    def test_extremos_0_y_1(self):
        assert self.clf.clasificar_riesgo(0.0) == EtiquetaRiesgo.BAJA
        assert self.clf.clasificar_riesgo(1.0) == EtiquetaRiesgo.ALTA


# ---------------------------------------------------------------------------
# Property-based: invariantes que deben valer para *cualquier* input válido
# ---------------------------------------------------------------------------

@settings(max_examples=300)
@given(umbral=_floats_libres, proba1=_floats_libres, proba2=_floats_libres)
def test_decision_binaria_es_monotona(umbral, proba1, proba2):
    """decision_binaria es una función escalón sobre proba: si proba1 <= proba2,
    la decisión de proba1 nunca puede ser 'más riesgosa' (mayor) que la de proba2.
    No debería depender de que umbral esté en [0,1]."""
    assume(proba1 <= proba2)
    clf = RiskClassifier(_FakeRiskConfig(umbral_decision=umbral, umbral_bajo=0.0, umbral_medio=0.0))
    assert clf.decision_binaria(proba1) <= clf.decision_binaria(proba2)


@settings(max_examples=300)
@given(umbral_bajo=_floats_libres, umbral_medio=_floats_libres, proba1=_floats_libres, proba2=_floats_libres)
def test_clasificar_riesgo_es_monotona_incluso_con_config_invalida(umbral_bajo, umbral_medio, proba1, proba2):
    """Propiedad más fuerte de lo que el nombre del método promete: la estructura
    if/elif/else hace que clasificar_riesgo termine siendo monótona en proba
    *sin importar* si umbral_bajo <= umbral_medio o no (ver test de abajo sobre
    qué se rompe realmente con umbrales invertidos: no es la monotonicidad,
    es que MEDIA se vuelve inalcanzable)."""
    assume(proba1 <= proba2)
    clf = RiskClassifier(_FakeRiskConfig(umbral_decision=0.5, umbral_bajo=umbral_bajo, umbral_medio=umbral_medio))
    r1 = clf.clasificar_riesgo(proba1)
    r2 = clf.clasificar_riesgo(proba2)
    assert _RANK[r1] <= _RANK[r2]


@settings(max_examples=200)
@given(umbral_bajo=_floats_libres, umbral_medio=_floats_libres, proba=_floats_libres)
def test_clasificar_riesgo_es_total_y_nunca_lanza(umbral_bajo, umbral_medio, proba):
    """clasificar_riesgo debe devolver siempre uno de los 3 valores del enum,
    para cualquier combinación de umbrales y proba (incluidas configuraciones
    'inválidas'), y nunca lanzar una excepción."""
    clf = RiskClassifier(_FakeRiskConfig(umbral_decision=0.5, umbral_bajo=umbral_bajo, umbral_medio=umbral_medio))
    resultado = clf.clasificar_riesgo(proba)
    assert resultado in (EtiquetaRiesgo.BAJA, EtiquetaRiesgo.MEDIA, EtiquetaRiesgo.ALTA)


@given(umbral_bajo=_umbrales, umbral_medio=_umbrales)
def test_media_inalcanzable_cuando_umbrales_estan_invertidos_o_iguales(umbral_bajo, umbral_medio):
    """BUG DE NEGOCIO DOCUMENTADO (no un crash): si umbral_bajo >= umbral_medio,
    la rama `umbral_bajo < proba <= umbral_medio` queda vacía por construcción y
    ningún cliente puede recibir la etiqueta MEDIA -- salta directo de BAJA a ALTA.
    RiskClassifier no valida esta precondición sobre su config, así que si algún
    día se permite cargar RiskConfig desde un archivo editable a mano, un typo en
    los umbrales degrada silenciosamente el modelo de 3 niveles a uno de 2.
    Este test falla (a propósito) si en el futuro se agrega esa validación --
    en ese punto hay que reemplazarlo por un test que espere que la construcción
    de una config inválida falle explícitamente.
    """
    assume(umbral_bajo >= umbral_medio)
    clf = RiskClassifier(_FakeRiskConfig(umbral_decision=0.5, umbral_bajo=umbral_bajo, umbral_medio=umbral_medio))
    etiquetas_posibles = {clf.clasificar_riesgo(p / 20) for p in range(0, 21)}
    assert EtiquetaRiesgo.MEDIA not in etiquetas_posibles


def test_decision_binaria_y_clasificar_riesgo_son_independientes():
    """decision_binaria usa umbral_decision; clasificar_riesgo usa umbral_bajo/medio.
    Son dos ejes de negocio distintos (decisión binaria de aprobar/rechazar vs.
    etiqueta informativa de riesgo) y no deberían estar acoplados: un cambio en
    umbral_decision no debe afectar la etiqueta de riesgo y viceversa."""
    base = dict(umbral_bajo=0.3, umbral_medio=0.7)
    clf_a = RiskClassifier(_FakeRiskConfig(umbral_decision=0.1, **base))
    clf_b = RiskClassifier(_FakeRiskConfig(umbral_decision=0.9, **base))
    proba = 0.5
    assert clf_a.clasificar_riesgo(proba) == clf_b.clasificar_riesgo(proba)
    # pero sí puede (y en este caso debe) diferir la decisión binaria
    assert clf_a.decision_binaria(proba) != clf_b.decision_binaria(proba)
