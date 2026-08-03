import pandas as pd
from app.config import ProcessingConfig
from app.validador import Validador


class Preprocessor:
    def __init__(
        self,
        *,
        features: list[str] | None,
        medianas: pd.Series,
        config: ProcessingConfig,
        validador: Validador | None
    ):
        self.features = features
        self.medianas = medianas
        self.config = config
        self.validador = validador

    @classmethod
    def para_entrenamiento(cls, *, medianas: pd.Series, config: ProcessingConfig, validador: Validador) -> "Preprocessor":
        return cls(features=None, medianas=medianas, config=config, validador=validador)

    @classmethod
    def para_inferencia(cls, *, features: list[str], medianas: pd.Series, config: ProcessingConfig) -> "Preprocessor":
        return cls(features=features, medianas=medianas, config=config, validador=None)

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
        if self.validador is not None:
            data_clientes_transformada = self.validador.validar(data_clientes_transformada)
        data_clientes_transformada = self._imputar(data_clientes_transformada)
        data_clientes_transformada = self._encoding(data_clientes_transformada)
        columnas_con_nan = data_clientes_transformada.columns[
            data_clientes_transformada.isna().any()
        ].tolist()
        if columnas_con_nan:
            raise RuntimeError(f"NaNs en output. Columnas afectadas: {columnas_con_nan}")
        return data_clientes_transformada