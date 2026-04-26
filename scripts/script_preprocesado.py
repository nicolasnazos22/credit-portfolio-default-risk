from pathlib import Path
import pandas as pd
def preprocesar(datos_clientes):
    LIMITE_EDAD = 90
    LIMITE_EXP_LABORAL = 60
    datos_clientes = datos_clientes.query("person_emp_length < @LIMITE_EXP_LABORAL and person_age < @LIMITE_EDAD") #defino universo de datos razonable para el modelo
    mediana = datos_clientes.median(numeric_only=True)
    datos_clientes = datos_clientes.fillna(mediana) #por simplicidad del modelo, dado que el foco es crear un producto de ingenieria de software, uso la mediana global. Lo ideal sin embargo es usar la mediana por grupo (grupo A, B, C, etc)
    datos_clientes_preprocesados = pd.get_dummies(datos_clientes, drop_first=False) #one hot encoding para convertir variables nominales en vectores que xgboost puede procesar
    return datos_clientes_preprocesados