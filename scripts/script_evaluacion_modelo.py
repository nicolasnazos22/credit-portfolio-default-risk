from pathlib import Path
import sys
ROOT_PATH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_PATH))
import joblib
from sklearn.metrics import average_precision_score, recall_score, precision_score
import pandas as pd
from datetime import datetime
import json
MODEL_PATH = Path(__file__).resolve().parent.parent / "model"
from app.schemas import Metricas
UMBRAL = 0.20
def evaluacion_modelo():
    modelo = joblib.load(MODEL_PATH / "modelo_scoring.joblib")
    features_test = pd.read_parquet(MODEL_PATH / "features_test.parquet")
    target_test = pd.read_parquet(MODEL_PATH / "target_test.parquet").values.ravel()
    proba = modelo.predict_proba(features_test)[:, 1]
    prediccion = (proba >= UMBRAL).astype(int)
    recall = recall_score(target_test, prediccion, pos_label=1)
    pr_auc = average_precision_score(target_test, proba)
    precision = precision_score(target_test, prediccion, pos_label=1)
    metricas = Metricas(timestamp = datetime.now(),
                        recall_default = recall,
                        precision_default = precision,
                        pr_auc = pr_auc
    )
    with open(MODEL_PATH / "metricas_modelo.json", "w") as f:
        json.dump(metricas.model_dump(), f, default=str, indent=6)
    print("volcando metricas a json")
    return metricas
if __name__ == "__main__":
    evaluacion_modelo()
