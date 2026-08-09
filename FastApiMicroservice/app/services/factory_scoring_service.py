import joblib
import shap as sh
from pathlib import Path

from app.core.config import RiskConfig
from app.services.SklearnPredictor import SklearnPredictor
from app.services.ShapTreeExplainer import ShapTreeExplainer
from app.services.Risk_classifier import RiskClassifier
from app.services.ScoringService import ScoringService
from app.processing.preprocessor import Preprocessor

# Rutas hardcodeadas. TODO: configurarlas desde variables de entorno
BASE_DIR = Path("model")
MODEL_PATH = BASE_DIR / "modelo_scoring.joblib"
CONFIG_PATH = BASE_DIR / "config.joblib"
MEDIANAS_PATH = BASE_DIR / "medianas.joblib"
"""
aca ocurre la magia. Basicamente el siguiente metodo crea el scoring service inyectandole todas sus dependencias
Se ejecuta durante el lifespan de fastapi


"""
def construir_scoring_service() -> ScoringService:
    # instancio la configuracion definida 
    config = RiskConfig()
    
    # 1. Carga de artefactos
    modelo_nativo = joblib.load(MODEL_PATH)
    config = joblib.load(CONFIG_PATH)
    medianas = joblib.load(MEDIANAS_PATH)
    
    # 2. instancio el explainer de shap
    explainer_nativo = sh.TreeExplainer(modelo_nativo)
    
    # 3. instanciacion del predictor
    predictor = SklearnPredictor(modelo=modelo_nativo)
    
    explainer = ShapTreeExplainer(
        explainer=explainer_nativo, 
        config=config
    )
    preprocesador = Preprocessor(medianas=medianas, config=config) 
    clasificador = RiskClassifier(configuracion=config)
    columnas_entrenamiento = list(preprocesador.feature_names_in_)
    
    # 4. Inyección de dependencias
    return ScoringService(
        preprocesador=preprocesador,
        predictor=predictor,
        clasificador=clasificador,
        explainer=explainer,
        columnas_entrenamiento=columnas_entrenamiento
    )