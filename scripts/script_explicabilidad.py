from pathlib import Path
import sys
ROOT_PATH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_PATH))
import joblib
import shap as sh
import pandas as pd
import matplotlib.pyplot as plt
MODEL_PATH = Path(__file__).resolve().parent.parent / "model"
def explicabilidad():
    try:
        modelo = joblib.load(MODEL_PATH / "modelo_scoring.joblib")
        features_test = pd.read_parquet(MODEL_PATH / "features_test.parquet")
    except FileNotFoundError as e:
        print(f"Error: Archivo no encontrado: {e}")
        return
    explainer = sh.TreeExplainer(modelo)
    valores_shap = explainer.shap_values(features_test) 
    sh.summary_plot(
        valores_shap,
        features_test,
        max_display=20,        
        plot_size=None,       
        alpha=0.5,            
       
    )
    return
   
if __name__ == "__main__":
    explicabilidad() 