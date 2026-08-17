"""
Tests de construir_scoring_service (factory_scoring_service.py).

Esta función no tiene lógica de negocio propia -- es 100% wiring de dependencias
(carga de artefactos + instanciación + inyección). El contrato que importa acá es:
"cada componente recibe exactamente la dependencia que le corresponde, construida
a partir de los artefactos cargados". Se mockean joblib.load, shap.TreeExplainer y
Preprocessor para no depender de artefactos .joblib reales ni de la implementación
de Preprocessor (no provista) -- lo que se testea es el cableado, no el contenido
de cada pieza (eso ya lo cubren los demás archivos de test).
"""
from unittest.mock import MagicMock, call

import app.services.factory_scoring_service as factory_module
from app.services.factory_scoring_service import construir_scoring_service, MODEL_PATH, CONFIG_PATH, MEDIANAS_PATH
from app.services.SklearnPredictor import SklearnPredictor
from app.services.ShapTreeExplainer import ShapTreeExplainer
from app.services.Risk_classifier import RiskClassifier
from app.services.ScoringService import ScoringService


def test_carga_los_tres_artefactos_desde_las_rutas_declaradas(monkeypatch):
    modelo_nativo, config, medianas = object(), object(), object()
    joblib_load_mock = MagicMock(side_effect=[modelo_nativo, config, medianas])
    monkeypatch.setattr(factory_module.joblib, "load", joblib_load_mock)
    monkeypatch.setattr(factory_module.sh, "TreeExplainer", MagicMock(return_value=object()))
    monkeypatch.setattr(factory_module, "Preprocessor", MagicMock(return_value=MagicMock(feature_names_in_=[])))

    construir_scoring_service()

    # el orden importa: modelo, config, medianas (así está escrito el código)
    assert joblib_load_mock.call_args_list == [call(MODEL_PATH), call(CONFIG_PATH), call(MEDIANAS_PATH)]


def test_cada_componente_recibe_la_dependencia_correcta(monkeypatch):
    modelo_nativo = object()
    config = object()
    medianas = object()
    explainer_nativo = object()
    columnas_esperadas = ["a", "b", "c"]

    monkeypatch.setattr(factory_module.joblib, "load", MagicMock(side_effect=[modelo_nativo, config, medianas]))
    tree_explainer_mock = MagicMock(return_value=explainer_nativo)
    monkeypatch.setattr(factory_module.sh, "TreeExplainer", tree_explainer_mock)
    preprocesador_fake = MagicMock(feature_names_in_=columnas_esperadas)
    preprocessor_cls_mock = MagicMock(return_value=preprocesador_fake)
    monkeypatch.setattr(factory_module, "Preprocessor", preprocessor_cls_mock)

    service = construir_scoring_service()

    # shap.TreeExplainer se construye con el modelo nativo, no con nada más
    tree_explainer_mock.assert_called_once_with(modelo_nativo)

    # Preprocessor recibe medianas + config, tal cual salieron de joblib
    preprocessor_cls_mock.assert_called_once_with(medianas=medianas, config=config)

    assert isinstance(service, ScoringService)
    assert isinstance(service.predictor, SklearnPredictor)
    assert service.predictor.modelo is modelo_nativo

    assert isinstance(service.explainer, ShapTreeExplainer)
    assert service.explainer.explainer is explainer_nativo
    assert service.explainer.config is config

    assert isinstance(service.clasificador, RiskClassifier)
    assert service.clasificador.configuracion is config

    assert service.preprocesador is preprocesador_fake
    # columnas_entrenamiento es list(feature_names_in_) -- una copia, no la misma lista
    assert service.columnas_entrenamiento == columnas_esperadas
    assert service.columnas_entrenamiento is not columnas_esperadas


def test_columnas_entrenamiento_se_copia_como_lista_nueva(monkeypatch):
    """list(preprocesador.feature_names_in_) debe funcionar aunque feature_names_in_
    sea un array de numpy (lo típico en sklearn), no solo una lista de Python."""
    import numpy as np
    monkeypatch.setattr(factory_module.joblib, "load", MagicMock(side_effect=[object(), object(), object()]))
    monkeypatch.setattr(factory_module.sh, "TreeExplainer", MagicMock(return_value=object()))
    preprocesador_fake = MagicMock(feature_names_in_=np.array(["f1", "f2", "f3"]))
    monkeypatch.setattr(factory_module, "Preprocessor", MagicMock(return_value=preprocesador_fake))

    service = construir_scoring_service()

    assert service.columnas_entrenamiento == ["f1", "f2", "f3"]
    assert isinstance(service.columnas_entrenamiento, list)


def test_la_instanciacion_inicial_de_riskconfig_es_codigo_muerto(monkeypatch):
    """BUG / CODE SMELL DOCUMENTADO: la función arranca con `config = RiskConfig()`
    y dos líneas después lo pisa con `config = joblib.load(CONFIG_PATH)`. Ese primer
    RiskConfig() nunca se usa. Este test no verifica una regla de negocio -- deja
    registrado que la construcción ocurre igual (con el costo/riesgo que eso implica:
    si RiskConfig() alguna vez pasa a requerir argumentos obligatorios, esta línea
    hace explotar la factory ANTES de siquiera intentar cargar los artefactos reales,
    por una instancia que de todos modos se iba a descartar). Si se limpia el código
    muerto, este test debe borrarse (o falla, como corresponde)."""
    riskconfig_mock = MagicMock(return_value="config_descartada")
    monkeypatch.setattr(factory_module, "RiskConfig", riskconfig_mock)
    monkeypatch.setattr(factory_module.joblib, "load", MagicMock(side_effect=[object(), object(), object()]))
    monkeypatch.setattr(factory_module.sh, "TreeExplainer", MagicMock(return_value=object()))
    monkeypatch.setattr(factory_module, "Preprocessor", MagicMock(return_value=MagicMock(feature_names_in_=[])))

    construir_scoring_service()

    riskconfig_mock.assert_called_once_with()
