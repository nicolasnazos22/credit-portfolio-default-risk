from pathlib import Path
import pandas as pd
import joblib
from app.schemas import CreditRiskResponse
from app.config import RiskConfig
from app.preprocessor import Preprocessor
import shap as sh

class ScoringService:
    def __init__(self, model_path: Path, config: RiskConfig):
        self.config = config
        self.modelo = joblib.load(model_path / "modelo_scoring.joblib")
        self.columnas_entrenamiento = joblib.load(model_path / "columnas_dataset.joblib")
        
        # Cargamos artefactos para procesar los datos de inferencia
        medianas = joblib.load(model_path / "medianas.joblib")
        config_prep = joblib.load(model_path / "config.joblib")
        
        self.preprocesador = Preprocessor.para_inferencia(
            features=self.columnas_entrenamiento,
            medianas=medianas,
            config=config_prep
        )
        
        self.explainer = sh.TreeExplainer(self.modelo)
    
    def _calcular_decision_binaria(self, proba: float) -> int:
        return 1 if proba >= self.config.umbral_decision else 0

    def _clasificar_riesgo(self, proba: float) -> str:
        if proba <= self.config.umbral_bajo:
            return "BAJA"
        elif proba <= self.config.umbral_medio:
            return "MEDIA"
        else:
            return "ALTA"

    def _calcular_impacto_shap(self, df_procesado: pd.DataFrame) -> dict:
        valores_shap = self.explainer.shap_values(df_procesado)
        
        # Dependiendo de la versión de SHAP, puede devolver una lista o un array
        impactos = valores_shap[1][0] if isinstance(valores_shap, list) else valores_shap[0]
        
        serie_impactos = pd.Series(impactos, index=self.columnas_entrenamiento)
        top_features = serie_impactos.abs().nlargest(self.config.cantidad_features).index
        
        return serie_impactos[top_features].round(4).to_dict()

    def predecir(self, payload_cliente: dict) -> CreditRiskResponse:
        df_crudo = pd.DataFrame([payload_cliente])
        
        # Transformamos los datos replicando la lógica exacta del entrenamiento
        df_procesado = self.preprocesador.transformar(df_crudo)
        
        proba = float(self.modelo.predict_proba(df_procesado)[:, 1][0])
        decision = self._calcular_decision_binaria(proba)
        etiqueta = self._clasificar_riesgo(proba)
        explicacion = self._calcular_impacto_shap(df_procesado)
        
        return CreditRiskResponse.armar_respuesta(
            probabilidad_default=proba, 
            etiqueta=etiqueta, 
            prediccion_default=decision,
            explicacion=explicacion
        )