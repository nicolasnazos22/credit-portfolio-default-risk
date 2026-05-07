import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from pathlib import Path
from preprocessor import Preprocessor
from config import ProcessingConfig
from logging import getLogger
PATH_ROOT = Path(__file__).resolve().parent.parent
PATH_DATA = PATH_ROOT / "data"
PATH_CSV = PATH_DATA / "credit_risk_dataset.csv"
PATH_MODEL = PATH_ROOT / "model"
def entrenar_modelo():
    PATH_MODEL.mkdir(exist_ok=True)
    log_metricas = getLogger(__name__)
    datos_clientes = pd.read_csv(PATH_CSV)
    datos_training_crudos, datos_test_crudos  = train_test_split(
        datos_clientes, test_size=0.2, random_state=42, stratify=datos_clientes["loan_status"]
    )
    medianas = datos_training_crudos.select_dtypes(include="number").median() #calculo la mediana que voy a usar para imputar despues de hacer el split para prevenir data leakage
    config = ProcessingConfig()
    preprocessor = Preprocessor.para_entrenamiento(medianas=medianas, config=config)
    training_transformado = preprocessor.transformar(datos_training_crudos)
    feature_matrix = training_transformado.drop('loan_status', axis=1)
    target_training  = training_transformado['loan_status']
    preprocessor_inferencia = Preprocessor.para_inferencia(
        features=feature_matrix.columns.tolist(),
        medianas=medianas,
        config=config
    )
    test_transformado = preprocessor_inferencia.transformar(datos_test_crudos)
    features_test = test_transformado.drop("loan_status", axis=1)
    target_test = test_transformado["loan_status"]

    constraints = {
    'person_income': -1,
    'loan_amnt': 1,
    'loan_int_rate': 1,
    'loan_percent_income': 1,
    'person_emp_length': -1
}
    neg = len(target_training[target_training == 0])
    pos = len(target_training[target_training == 1]) #conteo de cada clase del entrenamiento. En el caso del negocio de creditos tiene sentido asumir que va a haber mas creditos pagados que defaults.
    monotonic_tuple = tuple(constraints.get(feature, 0) for feature in feature_matrix.columns) #las monotonic constrains son para que el modelo respete invariantes economicos: a mayor ingreso, menor proba de default, 
# a mayor monto de credito, mayor tasa de interes y mayor ratio prestamo/ingresos mayor proba de default
    
    modelo = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, monotone_constraints = monotonic_tuple, eval_metric='logloss', scale_pos_weight=neg/pos, random_state=42)
    modelo.fit(feature_matrix, target_training)
    predicciones_test = modelo.predict(features_test)
    log_metricas.info("Metricas evaluacion modelo \n%s ", classification_report(target_test, predicciones_test))
    joblib.dump(modelo, PATH_MODEL / "modelo_scoring.joblib")
    joblib.dump(feature_matrix.columns.tolist(), PATH_MODEL / "columnas_dataset.joblib")
    joblib.dump(medianas, PATH_MODEL / "medianas.joblib")
    joblib.dump(config, PATH_MODEL / "config.joblib")
    features_test.to_parquet(PATH_MODEL / "features_test.parquet")
    target_test.to_frame().to_parquet(PATH_MODEL / "target_test.parquet")
    return modelo
if __name__ == "__main__":
    entrenar_modelo()
