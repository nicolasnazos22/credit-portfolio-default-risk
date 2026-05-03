from pydantic import Field
from pydantic_settings import BaseSettings
class RiskConfig(BaseSettings):
    umbral_decision: float = 0.3
    umbral_bajo: float = 0.2
    umbral_medio: float = 0.4
    cantidad_features: int = Field(
        default =5,
        ge =3,
        description="cantidad de variables a mostrar en el informa de explicabilidad para el asesor de riesgo"
    )
    class Config:
        env_prefix = "RISK_"
        env_prefix = "EXPLAINABILITY_FEATURES"