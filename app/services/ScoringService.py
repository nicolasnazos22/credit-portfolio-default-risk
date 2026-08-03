from app.services.interfaces import ModelPredictor, ModelExplainer, RiskClassifier
import pandas as pd
from app.schemas import CreditRiskResponse
from app.preprocessor import Preprocessor
from dataclasses import dataclass
@dataclass(frozen=True)
class ScoringService:
    preprocesador: Preprocessor
    predictor: ModelPredictor
    explainer: ModelExplainer
    columnas_entrenamiento: list[str]
    clasificador: RiskClassifier

    def predecir(self, payload_cliente: dict) -> CreditRiskResponse:
        try:
            df_crudo = pd.DataFrame([payload_cliente])
        
        # 1. Transformación
            df_procesado = self.preprocesador.transformar(df_crudo)
        
        # 2. Predicción Pura
            proba = self.predictor.predecir_probabilidad(df_procesado)
        except Exception as error_librerias:
            raise RuntimeError(f"Error procesando el modelo: {str(error_librerias)}")
            
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