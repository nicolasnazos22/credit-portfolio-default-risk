from app.services.interfaces import ModelPredictor, ModelExplainer, RiskClassifier
import pandas as pd
from app.schemas import CreditRiskResponse
from app.preprocessor import Preprocessor
class ScoringService:
    def __init__(
        self, 
        preprocesador, 
        predictor: ModelPredictor,
        clasificador: RiskClassifier,
        explainer: ModelExplainer,
        columnas_entrenamiento: list[str]
    ):
        self.preprocesador = preprocesador
        self.predictor = predictor
        self.clasificador = clasificador
        self.explainer = explainer
        self.columnas_entrenamiento = columnas_entrenamiento

    def predecir(self, payload_cliente: dict) -> CreditRiskResponse:
        df_crudo = pd.DataFrame([payload_cliente])
        
        # 1. Transformación
        df_procesado = self.preprocesador.transformar(df_crudo)
        
        # 2. Predicción Pura
        proba = self.predictor.predecir_probabilidad(df_procesado)
        
        # 3. Reglas de Negocio
        decision = self.clasificador.decision_binaria(proba)
        etiqueta = self.clasificador.clasificar_riesgo(proba)
        
        # 4. Interpretabilidad
        explicacion = self.explainer.calcular_impacto(df_procesado, self.columnas_entrenamiento)
        
        # 5. Salida
        return CreditRiskResponse.armar_respuesta(
            probabilidad_default=proba, 
            etiqueta=etiqueta, 
            prediccion_default=decision,
            explicacion=explicacion
        )