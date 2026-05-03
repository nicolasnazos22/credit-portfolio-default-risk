from pathlib import Path
import pandas as pd
import joblib
from app.schemas import CreditRiskResponse
from app.config import RiskConfig
import shap as sh
MODEL_PATH = Path(__file__).resolve().parent.parent / "model"
class ScoringService:
    def __init__(self, model_path:Path, config: RiskConfig):
        self.model = joblib.load(model_path / "modelo_scoring.joblib")
        self.features_columnas = joblib.load(model_path / "columnas_dataset.joblib")
        self.config = config
        self.explainer = sh.TreeExplainer(self.model) #
    
    def obtener_proba_default(self, proba: float) -> int:
        return 1 if proba >= self.config.umbral_decision else 0

    def obtener_etiqueta_riesgo(self, probabilidad: float) -> str:
        if probabilidad <= self.config.umbral_bajo:
            return "BAJA"
        elif probabilidad <= self.config.umbral_medio:
            return "MEDIA"
        else:
            return "ALTA"
    def explicar_decision(self, dataframe_cliente_final: pd.DataFrame, ) -> dict:
        valores_shap = self.explainer.shap_values(dataframe_cliente_final)
        if isinstance(valores_shap, list):
            features_default = valores_shap[1][0]
        else:
            features_default = valores_shap[0]
        features_impacto = pd.Series(features_default, index=self.features_columnas)
        top_features_impacto = features_impacto.abs().nlargest(self.config.cantidad_features).index
        return features_impacto[top_features_impacto].round(4).to_dict()



    def predecir(self, datos_cliente:dict):
        dataframe_cliente = pd.DataFrame([datos_cliente])
        dataframe_cliente_final = dataframe_cliente.reindex(columns=self.features_columnas, fill_value=0) #aseguro orden exacto de las columnas del entrenamiento y lleno con 0 las features faltantes
        proba_default = float(self.model.predict_proba(dataframe_cliente_final)[:, 1][0])
        prediccion = self.obtener_proba_default(proba_default)
        etiqueta = self.obtener_etiqueta_riesgo(proba_default)
        explicacion = self.explicar_decision(dataframe_cliente_final)
        return CreditRiskResponse.armar_respuesta(
                                                    probabilidad_default=proba_default, 
                                                    etiqueta=etiqueta, 
                                                    prediccion_default=prediccion,
                                                    explicacion = explicacion
        )
