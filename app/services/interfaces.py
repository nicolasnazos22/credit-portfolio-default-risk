from typing import Protocol
import pandas as pd
from app.domain.schemas import CreditRiskResponse
from app.core.config import RiskConfig

class ModelPredictor(Protocol):
    def predecir_probabilidad(self, df_procesado: pd.DataFrame) -> float:
        ...

class RiskClassifier(Protocol):
    def decision_binaria(self, proba: float) -> int:
        ...
    def clasificar_riesgo(self, proba: float) -> str:
        ...

class ModelExplainer(Protocol):
    def calcular_impacto(self, df_procesado: pd.DataFrame, columnas: list[str]) -> dict:
        ...