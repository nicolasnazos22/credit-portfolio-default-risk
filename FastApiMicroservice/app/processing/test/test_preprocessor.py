import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings, strategies as st

from app.processing.src.preprocessor import Preprocessor  
from app.core.config import ProcessingConfig 
from doubles import ValidadorQueFalla
from estrategias_dataframes import MEDIANAS, MEDIANAS_COLS, numeric_df_strategy, mixed_df_strategy


class TestConstructores:
    def test_para_entrenamiento_setea_features_none_y_usa_validador(self, medianas, config, validador_ok):
        pre = Preprocessor.para_entrenamiento(medianas=medianas, config=config, validador=validador_ok)
        assert pre.features is None
        assert pre.validador is validador_ok
        assert pre.medianas is medianas
        assert pre.config is config

    def test_para_inferencia_setea_features_y_validador_none(self, medianas, config):
        features = ["edad", "ingreso", "categoria_a"]
        pre = Preprocessor.para_inferencia(features=features, medianas=medianas, config=config)
        assert pre.features == features
        assert pre.validador is None


class TestValidador:
    def test_transformar_llama_a_validador_cuando_existe(self, medianas, config, validador_ok):
        pre = Preprocessor.para_entrenamiento(medianas=medianas, config=config, validador=validador_ok)
        df = pd.DataFrame({"edad": [30], "ingreso": [40000], "score": [600]})
        pre.transformar(df)
        assert validador_ok.llamado is True

    def test_transformar_no_llama_a_validador_cuando_es_none(self, medianas, config):
        pre = Preprocessor.para_inferencia(features=["edad"], medianas=medianas, config=config)
        df = pd.DataFrame({"edad": [30]})
        pre.transformar(df)

    def test_transformar_propaga_excepcion_del_validador(self, medianas, config):
        validador = ValidadorQueFalla("dato invalido")
        pre = Preprocessor.para_entrenamiento(medianas=medianas, config=config, validador=validador)
        df = pd.DataFrame({"edad": [30]})
        with pytest.raises(ValueError, match="dato invalido"):
            pre.transformar(df)


"""
testing usando casos de negocio conocidos
"""

class TestCasosDeNegocio:
    def test_categoria_no_vista_en_inferencia_termina_en_cero(self, medianas, config):
        features = ["edad", "ingreso", "score", "provincia_caba", "provincia_cordoba"]
        pre = Preprocessor.para_inferencia(features=features, medianas=medianas, config=config)
        df = pd.DataFrame({
            "edad": [30], "ingreso": [40000], "score": [600],
            "provincia": ["misiones"],
        })
        out = pre.transformar(df)
        assert out["provincia_caba"].iloc[0] == 0
        assert out["provincia_cordoba"].iloc[0] == 0
        assert set(out.columns) == set(features)

    def test_columna_categorica_ausente_por_completo_en_inferencia(self, medianas, config):
        features = ["edad", "provincia_caba"]
        pre = Preprocessor.para_inferencia(features=features, medianas=medianas, config=config)
        df = pd.DataFrame({"edad": [30]})
        out = pre.transformar(df)
        assert list(out.columns) == features
        assert out["provincia_caba"].iloc[0] == 0

    def test_columnas_numericas_con_nan_se_imputan_con_mediana(self, medianas, config):
        features = ["edad", "ingreso", "score"]
        pre = Preprocessor.para_inferencia(features=features, medianas=medianas, config=config)
        df = pd.DataFrame({"edad": [np.nan], "ingreso": [np.nan], "score": [700]})
        out = pre.transformar(df)
        assert out["edad"].iloc[0] == medianas["edad"]
        assert out["ingreso"].iloc[0] == medianas["ingreso"]

    def test_dataframe_vacio_de_filas_no_explota(self, medianas, config):
        features = ["edad"]
        pre = Preprocessor.para_inferencia(features=features, medianas=medianas, config=config)
        df = pd.DataFrame({"edad": pd.Series(dtype=float)})
        out = pre.transformar(df)
        assert list(out.columns) == features
        assert len(out) == 0

class TestPropiedadesImputacion:

    @given(df=numeric_df_strategy)
    @settings(max_examples=100)
    def test_imputar_no_deja_nans_en_columnas_numericas(self, df):
        pre = Preprocessor(features=None, medianas=MEDIANAS, config=ProcessingConfig(), validador=None)
        out = pre._imputar(df.copy())
        assert not out[MEDIANAS_COLS].isna().any().any()

    @given(
        valores=st.lists(
            st.one_of(st.none(), st.sampled_from(["a", "b", "c"])),
            min_size=1, max_size=20,
        )
    )
    @settings(max_examples=100)
    def test_imputar_categoricas_usa_desconocido(self, valores):
        df = pd.DataFrame({"categoria": valores})
        pre = Preprocessor(features=None, medianas=pd.Series(dtype=float), config=ProcessingConfig(), validador=None)
        out = pre._imputar(df.copy())
        assert not out["categoria"].isna().any()
        for original, imputado in zip(valores, out["categoria"]):
            if original is None:
                assert imputado == "desconocido"
            else:
                assert imputado == original


class TestPropiedadesEncoding:

    @given(df=mixed_df_strategy)
    @settings(max_examples=100)
    def test_encoding_inferencia_respeta_columnas_de_features_exactamente(self, df):
        features = ["edad", "categoria_a", "categoria_b", "categoria_x_nunca_vista"]
        pre = Preprocessor(features=features, medianas=MEDIANAS, config=ProcessingConfig(), validador=None)
        out = pre._encoding(df.copy())
        assert list(out.columns) == features

    @given(df=mixed_df_strategy)
    @settings(max_examples=100)
    def test_encoding_siempre_devuelve_float32(self, df):
        pre = Preprocessor(features=None, medianas=MEDIANAS, config=ProcessingConfig(), validador=None)
        out = pre._encoding(df.copy())
        assert all(dtype == np.float32 for dtype in out.dtypes)

    @given(df=mixed_df_strategy)
    @settings(max_examples=50)
    def test_encoding_entrenamiento_no_filtra_columnas_dummy(self, df):
        pre = Preprocessor(features=None, medianas=MEDIANAS, config=ProcessingConfig(), validador=None)
        out = pre._encoding(df.copy())
        esperado_min = {"edad"} | {f"categoria_{v}" for v in df["categoria"].unique()}
        assert esperado_min.issubset(set(out.columns))


class TestPropiedadesTransformarEndToEnd:

    @given(df=numeric_df_strategy)
    @settings(max_examples=50)
    def test_transformar_nunca_deja_nans_cuando_medianas_cubren_todo(self, df):
        features = MEDIANAS_COLS
        pre = Preprocessor.para_inferencia(features=features, medianas=MEDIANAS, config=ProcessingConfig())
        out = pre.transformar(df.copy())
        assert not out.isna().any().any()

    @given(df=numeric_df_strategy)
    @settings(max_examples=50)
    def test_transformar_es_deterministico_en_forma(self, df):
        features = MEDIANAS_COLS
        pre = Preprocessor.para_inferencia(features=features, medianas=MEDIANAS, config=ProcessingConfig())
        out1 = pre.transformar(df.copy())
        out2 = pre.transformar(df.copy())
        assert list(out1.columns) == list(out2.columns)

    def test_transformar_no_muta_el_dataframe_original(self, medianas, config):
        pre = Preprocessor.para_inferencia(features=["edad"], medianas=medianas, config=config)
        df_original = pd.DataFrame({"edad": [np.nan]})
        df_copia_para_comparar = df_original.copy(deep=True)
        pre.transformar(df_original)
        pd.testing.assert_frame_equal(df_original, df_copia_para_comparar)