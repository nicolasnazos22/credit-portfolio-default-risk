from pydantic import BaseModel, Field
from enum import Enum
from typing import Annotated
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
#formato de request
class CreditRiskRequest(BaseModel):
    person_age: Annotated[int, Field(ge=18, le=100)]
    person_income: Annotated[int, Field(ge=10000, description="ingreso anual en USD")]
    person_home_ownership: HomeOwnership
    person_emp_length: Annotated[float, Field(ge=0, le=60, description="años de empleo")]
    loan_intent: LoanIntent
    loan_grade: LoanGrade
    loan_amnt: Annotated[int, Field(ge=1000, le=50000, description="monto solicitado")]
    loan_int_rate: Annotated[float, Field(ge=5.0, le=25.0, description="tasa de interes")]
    loan_percent_income: Annotated[float, Field(ge=0.0, le=1.0, description="ratio monto solicitado/ingresos anuales")]
    cb_person_cred_hist_length: Annotated[int, Field(ge=0, le=60, description="historial crediticio en años")]
    cb_person_default_on_file: CbDefaultOnFile


class CreditRiskResponse(BaseModel):
    probabilidad_default: Annotated[float, Field(ge=0.0, le=1.0, description="probabilidad inferida de caer en default")]
    default_prediccion: Annotated[int, Field(description= "0 si no hay default, 1 si hay default. Binario")]
    etiqueta_riesgo: Annotated[str, Field(description = "BAJA, MEDIA, ALTA")]
    @classmethod
    def etiquetado_riesgo(cls, probabilidad_default: float, umbral: float = 0.2) -> "CreditRiskResponse":
        default_prediccion = int(probabilidad_default >= umbral)
        if probabilidad_default < 0.3:
            etiqueta = "BAJA"
        elif probabilidad_default <0.6:
            etiqueta = "MEDIA"
        else:
            etiqueta = "ALTA"
        return cls(
            probabilidad_default = round(probabilidad_default, 4),
            default_prediccion = default_prediccion,
            etiqueta_riesgo = etiqueta
        )
class CreditRiskBatchRequest(BaseModel):
    requests: Annotated[
        list[CreditRiskRequest],
        Field(min_length=2, max_length=1000, description="procesamiento batch de clientes"),

    ]
class CreditRiskBatchResponse(BaseModel):
    resultados: list[CreditRiskResponse]
    total: int
    total_defaults_detectados: int
    @classmethod 
    def from_responses(cls, respuestas: list [CreditRiskResponse]) -> "CreditRiskBatchResponse":
        return cls(
            resultados = respuestas,
            total = len(respuestas),
            total_defaults_detectados = sum(cliente.default_prediccion for cliente in respuestas)
        )