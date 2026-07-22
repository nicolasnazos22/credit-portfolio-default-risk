from dataclasses import dataclass
import pandas as pd
import shap as sh
from app.config import RiskConfig

@dataclass(frozen=True)
class ShapTreeExplainer:
    explainer: sh.TreeExplainer 
    config: RiskConfig

    def calcular_impacto(self, df_procesado: pd.DataFrame, columnas: list[str]) -> dict:
        valores_shap = self.explainer.shap_values(df_procesado)
        
        match valores_shap:
            case [_, clase_positiva]:
                impactos = clase_positiva[0]
            case _:
                impactos = valores_shap[0]
        
        serie_impactos = pd.Series(impactos, index=columnas)
        top_features = serie_impactos.abs().nlargest(self.config.cantidad_features).index
        
        return serie_impactos[top_features].round(4).to_dict()
