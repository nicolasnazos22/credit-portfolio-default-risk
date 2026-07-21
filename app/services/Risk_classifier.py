from dataclasses import dataclass
from app.config import RiskConfig
@dataclass(frozen=True)
class RiskClassifier:
    configuracion: RiskConfig
    def decision_binaria(self, proba: float):
        return 1 if proba >= self.configuracion.umbral_decision else 0
    def clasificar_riesgo(self, proba:float):
        if proba <= self.configuracion.umbral_bajo:
            return "BAJA"
        elif self.configuracion.umbral_bajo < proba <= self.configuracion.umbral_medio:
            return "MEDIA"
        return "ALTA"