import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from pathlib import Path
PATH_CSV_ROOT = Path(__file__).resolve().parent.parent
PATH_CSV = PATH_CSV_ROOT / "data" / "credit_risk_dataset.csv"
PATH_MODELS = PATH_CSV_ROOT / "models"
PATH_FEATURES_TEST = Path(__file__).resolve().parent.parent / "data" / "features_test.parquet"
PATH_TARGET_TEST = Path(__file__).resolve().parent.parent / "data" / "target_test.parquet"
def entrenar_modelo():
    PATH_MODELS.mkdir(exist_ok=True)
    datos_clientes = pd.read_csv(PATH_CSV)
    data_frame_clientes_preprocesado = preprocesar(datos_clientes)
    feature_matrix = data_frame_clientes_preprocesado.drop('loan_status', axis=1)
    target_vector = data_frame_clientes_preprocesado['loan_status']
    features_training, features_test, target_training, target_test = train_test_split(feature_matrix, target_vector, test_size=0.2, random_state=42, stratify=target_vector) #divido en train y test para poder validar el modelo
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
    modelo.fit(features_training, target_training)
    proba = modelo.predict_proba(features_test)[:, 1]
    UMBRAL = 0.20
    pred = (proba >= UMBRAL).astype(int)
    joblib.dump(modelo, PATH_MODELS / "modelo_scoring.joblib")
    joblib.dump(feature_matrix.columns.tolist(), PATH_MODELS / "columnas_dataset.joblib")
    features_test.to_parquet(PATH_FEATURES_TEST)
    target_test.to_frame().to_parquet(PATH_TARGET_TEST)
    return modelo

