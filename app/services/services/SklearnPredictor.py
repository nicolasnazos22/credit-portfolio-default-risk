from dataclasses import dataclass
from typing import Any
import pandas as pd
@dataclass(frozen=True)
class SklearnPredictor:
    modelo: Any
    def predecir_probabilidad(self, df_procesado: pd.DataFrame):
        return float(self.modelo.predict_proba(df_procesado)[:, 1][0])