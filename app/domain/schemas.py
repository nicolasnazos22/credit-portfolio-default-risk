from pydantic import BaseModel, Field, model_validator
from enum import Enum
from typing import Annotated, Literal
from datetime import datetime
#tipos enum primero:
class HomeOwnership(str, Enum):
    RENT = "RENT"
    OWN = "OWN"
    MORTGAGE = "MORTGAGE"
    OTHER = "OTHER"
class LoanIntent(str, Enum):
    PERSONAL = "PERSONAL"
    EDUCATION = "EDUCATION"
    HOMEIMPROVEMENT = "HOMEIMPROVEMENT"
    DEBTCONSOLIDATION = "DEBTCONSOLIDATION"
    MEDICAL = "MEDICAL"
    VENTURE = "VENTURE"
class LoanGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
class CbDefaultOnFile(str, Enum):
    Y = "Y"
    N = "N"
class EtiquetaRiesgo(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"

Proba = Annotated[float, Field(ge=0.0, le=1.0)]
class CreditRiskRequest(BaseModel):
    person_age: Annotated[int, Field(ge=18, le=100, description="edad del solicitante en años")]
    person_income: Annotated[int, Field(ge=10000, le=1000000, description="ingreso anual en USD")]
    person_home_ownership: HomeOwnership
    person_emp_length: Annotated[float, Field(ge=0, le=60, description="años de empleo")]
    loan_intent: LoanIntent
    loan_grade: LoanGrade
    loan_amnt: Annotated[int, Field(ge=1000, le=50000, description="monto solicitado")]
    loan_int_rate: Annotated[float, Field(ge=5.0, le=25.0, description="tasa de interes")]
    loan_percent_income: Annotated[float, Field(ge=0.0, le=1.0, description="ratio monto solicitado/ingresos anuales")]
    cb_person_cred_hist_length: Annotated[int, Field(ge=0, le=60, description="historial crediticio en años")]
    cb_person_default_on_file: CbDefaultOnFile, Field(description="indica si el solicitante tiene registrado default previo en su historial")
    @model_validator(mode="after")
    def logica_negocio_valida(self):
        edad_laboral = self.person_age - 16
        if self.person_emp_length > edad_laboral:
            raise ValueError("la experiencia laboral no puede ser superior a edad-16")
        if self.cb_person_cred_hist_length > edad_laboral-2:
            raise ValueError("No es posible pedir credito antes de los 18")
        return self


class CreditRiskResponse(BaseModel):
    probabilidad_default: Annotated[float, Field(ge=0.0, le=1.0, description="probabilidad inferida de caer en default")]
    default_prediccion: Annotated[Literal[0, 1], Field(description= "0 si no hay default, 1 si hay default. Binario")]
    etiqueta_riesgo: Annotated[EtiquetaRiesgo, Field(description = "BAJA, MEDIA, ALTA")]
    explicacion: Annotated[dict[str, float], Field(description="valores shap: atributos del cliente y su impacto en la prediccion")]
    @classmethod
    def armar_respuesta(cls, probabilidad_default: float, etiqueta: EtiquetaRiesgo, prediccion_default: int, explicacion: dict[str, float]) -> "CreditRiskResponse":
        return cls(
            probabilidad_default = round(probabilidad_default, 4),
            default_prediccion = prediccion_default,
            etiqueta_riesgo = etiqueta,
            explicacion = explicacion
        )
class PortfolioRiskSimulationRequest(BaseModel):
    # 1. Definimos el tipo base para las probabilidades
    cantidad_escenarios: Annotated[
        int, Field(
            ge=1000, 
            le=10000, 
            description="Cantidad de escenarios. Mínimo 1000 para convergencia, máximo 10000 para estabilidad."
        )
    ] = 10000
    requests: Annotated[
        list[Proba],
        Field(
            min_length=2, 
            max_length=1000, 
            description="Lista de probabilidades para simulación de Monte Carlo"
        )
    ]
class PortfolioRiskSimulationResponse(BaseModel):
    cantidad_simulaciones: Annotated[int, Field(description="cantidad total de simulaciones")]
    var_95: Annotated[float, Field(ge=0.0, description="cantidad maxima de defaults en el 95% de los escenarios simulados")]
    cvar_95: Annotated[float, Field(ge=0.0, description="Media de defaults en el peor 5% de los escenarios")]

    @classmethod
    def armar_respuesta(cls, simulaciones: int, var_95: int, cvar_95: int) -> "PortfolioRiskSimulationResponse":
        return cls(
            cantidad_simulaciones=simulaciones,
            var_95=float(var_95),
            cvar_95=float(cvar_95),
    )
            
class Metricas(BaseModel):
    timestamp: Annotated[datetime, Field(description="momento en que las metricas del modelo fueron registradas")]
    recall_default: Annotated[float, Field(ge=0.0, le=1.0, description="sensibilidad sobre la clase default")]
    precision_default: Annotated[float, Field(ge=0.0, le=1.0, description="precision de deteccion de defaults")]
    pr_auc: Annotated[float, Field(ge=0.0, le=1.0, description="area bajo la curva precision-recall")]


