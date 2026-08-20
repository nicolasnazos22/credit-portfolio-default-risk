from fastapi import FastAPI, Request, Depends
from app.services.src.factory_scoring_service import construir_scoring_service
from app.services.src.ScoringService import ScoringService
from app.services.src.MontecarloService import MontecarloService
from app.domain.schemas import CreditRiskRequest, CreditRiskResponse, PortfolioRiskSimulationRequest, PortfolioRiskSimulationResponse
from contextlib import asynccontextmanager
from typing import Annotated, TypeAlias

@asynccontextmanager
async def lifespan(app: FastAPI):
        # carga del modelo a la RAM al inicializar 
    app.state.scoring_service = construir_scoring_service()
    app.state.montecarlo_service = MontecarloService()
    yield
app = FastAPI(
    title="app de scoring de riesgo crediticio", 
    lifespan=lifespan
    )
def get_scoring_service(request: Request) -> ScoringService:
    return request.app.state.scoring_service
ScoringServiceDep: TypeAlias = Annotated[ScoringService, Depends(get_scoring_service)]
@app.post("/calcular", response_model=CreditRiskResponse)
def calcular(payload_cliente: CreditRiskRequest, servicio: ScoringServiceDep):
    datos_dict = payload_cliente.model_dump()
    return servicio.predecir(datos_dict)
def get_montecarlo_service(request: Request) -> MontecarloService:
    return request.app.state.montecarlo_service
MontecarloServiceDep: TypeAlias = Annotated[MontecarloService, Depends(get_montecarlo_service)]
@app.post("/simular", response_model= PortfolioRiskSimulationResponse)
def simular(payload_cliente: PortfolioRiskSimulationRequest, servicio: MontecarloServiceDep):
    return servicio.simular_riesgo_portfolio(probabilidades=payload_cliente.requests, cantidad_escenarios=payload_cliente.cantidad_escenarios)
