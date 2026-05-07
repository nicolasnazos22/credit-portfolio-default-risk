import pandas as pd
from config import ProcessingConfig

class Preprocessor:
    def __init__(
        self,
        *,
        features: list[str] | None,
        medianas: pd.Series,
        config: ProcessingConfig
    ):
        self.features = features
        self.medianas = medianas
        self.config = config

    @classmethod
    def para_entrenamiento(cls, *, medianas: pd.Series, config: ProcessingConfig) -> "Preprocessor":
        return cls(features=None, medianas=medianas, config=config)

    @classmethod
    def para_inferencia(cls, *, features: list[str], medianas: pd.Series, config: ProcessingConfig) -> "Preprocessor":
        return cls(features=features, medianas=medianas, config=config)
    
    def _validar(self, data_clientes: pd.DataFrame) -> pd.DataFrame:
        columnas_criticas = ["person_emp_length", "person_age"]
        data_clientes = data_clientes.dropna(subset=columnas_criticas)
        data_clientes_limpio = data_clientes[
            (data_clientes["person_emp_length"] < self.config.limite_exp) &
            (data_clientes["person_age"] < self.config.limite_edad) &
            (data_clientes["person_emp_length"] <= (data_clientes["person_age"] - 16)) &
            (data_clientes["loan_amnt"] > 0) &
            (data_clientes["person_income"] > 0)
        ].copy()

        if data_clientes_limpio.empty:
            raise ValueError("No hay registros válidos tras la validación.")

        return data_clientes_limpio

    def _imputar(self, data_clientes: pd.DataFrame) -> pd.DataFrame:
        numericas = data_clientes.select_dtypes(include="number").columns
        categoricas = data_clientes.select_dtypes(include="object").columns
        data_clientes[numericas] = data_clientes[numericas].fillna(self.medianas)
        data_clientes[categoricas] = data_clientes[categoricas].fillna("desconocido")
        return data_clientes

    def _encoding(self, data_clientes: pd.DataFrame) -> pd.DataFrame:
        data_clientes_encoded = pd.get_dummies(data_clientes, drop_first=False, dtype=int)
        if self.features is not None:
            data_clientes_encoded = data_clientes_encoded.reindex(
                columns=self.features,
                fill_value=0
            )

        return data_clientes_encoded.astype("float32")


    def transformar(self, data_clientes: pd.DataFrame) -> pd.DataFrame:
        data_clientes_transformada = data_clientes.copy(deep=True)
        data_clientes_transformada = self._validar(data_clientes_transformada)
        data_clientes_transformada = self._imputar(data_clientes_transformada)
        data_clientes_transformada = self._encoding(data_clientes_transformada)
        columnas_con_nan = data_clientes_transformada.columns[
            data_clientes_transformada.isna().any()
        ].tolist()
        if columnas_con_nan:
            raise RuntimeError(f"NaNs en output. Columnas afectadas: {columnas_con_nan}")

        return data_clientes_transformada