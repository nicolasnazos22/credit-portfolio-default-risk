import pandas as pd
from hypothesis import strategies as st
from hypothesis.extra.pandas import data_frames, column, range_indexes
 

#valores constantes usados en tests para testear imputacion de medianas
MEDIANAS_COLS = ["edad", "ingreso", "score"]
MEDIANAS = pd.Series({"edad": 35.0, "ingreso": 50000.0, "score": 650.0})

#generacion de dataframes con valores faltantes para testear imputacion mediana
 
numeric_df_strategy = data_frames(
    columns=[
        column("edad", elements=st.one_of(st.none(), st.floats(0, 100, allow_nan=False))),
        column("ingreso", elements=st.one_of(st.none(), st.floats(0, 1_000_000, allow_nan=False))),
        column("score", elements=st.one_of(st.none(), st.floats(0, 1000, allow_nan=False))),
    ],
    index=range_indexes(min_size=1, max_size=20),
)
 
#generacion de dataframe con columnas categoricas y numericas para testear one hot encoding
 
categorical_values = st.sampled_from(["a", "b", "c", "d"])
 
mixed_df_strategy = data_frames(
    columns=[
        column("edad", elements=st.floats(0, 100, allow_nan=False)),
        column("categoria", elements=categorical_values),
    ],
    index=range_indexes(min_size=1, max_size=15),
)
 