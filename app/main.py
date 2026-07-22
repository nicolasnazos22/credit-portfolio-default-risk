from fastapi import FastAPI, Request, Depends
from app.services.factory_scoring_service import construir_scoring_service
from app.services.ScoringService import ScoringService
from app.schemas import CreditRiskRequest, CreditRiskResponse
from contextlib import asynccontextmanager
from typing import Annotated, TypeAlias

@asynccontextmanager
async def lifespan(app: FastAPI):
        # carga del modelo a la RAM al inicializar 
    app.state.scoring_service = construir_scoring_service()
    yield
    app.state.scoring_service = None
app = FastAPI(
    title="app de scoring de riesgo crediticio", 
    lifespan=lifespan
    )
def get_scoring_service(request: Request) -> ScoringService:
    return request.app.state.scoring_service
ScoringServiceDep: TypeAlias = Annotated[ScoringService, Depends(get_scoring_service)]
@app.post("/calcular", response_model=CreditRiskResponse)
def calcular(payload_cliente: CreditRiskRequest, servicio: ScoringServiceDep):
    servicio =  getattr(app.state, "scoring_service", None)
    datos_dict = payload_cliente.model_dump()
    return servicio.predecir(datos_dict)
