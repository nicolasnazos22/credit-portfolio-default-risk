from dataclasses import dataclass
from app.core.config import RiskConfig
from app.domain.schemas import EtiquetaRiesgo
@dataclass(frozen=True)
class RiskClassifier:
    configuracion: RiskConfig
    def decision_binaria(self, proba: float):
        return 1 if proba >= self.configuracion.umbral_decision else 0
    def clasificar_riesgo(self, proba:float):
        if proba <= self.configuracion.umbral_bajo:
            return EtiquetaRiesgo.BAJA
        elif self.configuracion.umbral_bajo < proba <= self.configuracion.umbral_medio:
            return EtiquetaRiesgo.MEDIA
        return EtiquetaRiesgo.ALTA