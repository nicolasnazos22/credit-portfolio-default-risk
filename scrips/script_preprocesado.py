from pathlib import Path
import pandas as pd
def preprocesar():
    PATH_CSV_ROOT = Path(__file__).resolve().parent.parent
    PATH_CSV = PATH_CSV_ROOT / "data" / "credit_risk_dataset.csv"
    LIMITE_EDAD = 90
    LIMITE_EXP_LABORAL = 60
    datos_clientes = pd.read_csv(PATH_CSV)
    datos_clientes = datos_clientes.query("person_emp_length < @LIMITE_EXP_LABORAL and person_age < @LIMITE_EDAD") #defino universo de datos razonable para el modelo
    mediana = datos_clientes.median(numeric_only=True)
    datos_clientes = datos_clientes.fillna(mediana)
    datos_clientes_preprocesados = pd.get_dummies(datos_clientes, drop_first=False) #one hot encoding para convertir variables nominales en vectores que xgboost puede procesar
    return datos_clientes_preprocesados