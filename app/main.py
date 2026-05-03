from fastapi import FastAPI, HTTPException
from pathlib import Path
from app.services.ScoringService import ScoringService
from app.schemas import CreditRiskRequest, CreditRiskResponse
from contextlib import asynccontextmanager
from app.config import RiskConfig
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
#Paths:
ROOT_PATH = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT_PATH / "model"

#voy a usar lifespan pattern
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app_config = RiskConfig()
        app.state.scoring_service = ScoringService(model_path=MODEL_PATH, config = app_config)
        logger.info("carga exitosa del modelo")
    except Exception as e:
        logger.error("fallo en la carga del modelo, procediendo a cerrar", exc_info=True)
        raise e
    yield
    app.state.scoring_service = None
app = FastAPI(
    title="app de scoring de riesgo crediticio", 
    lifespan=lifespan
    )
@app.post("/calcular", response_model=CreditRiskResponse)
async def calcular(request: CreditRiskRequest):
    servicio =  getattr(app.state, "scoring_service", None)
    if not servicio:
        raise HTTPException(
            status_code= 503, 
            detail="problema cargando el modelo. Operacion abortada"
            )
    return servicio.predecir(request.model_dump())
