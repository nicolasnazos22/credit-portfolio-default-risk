import pandas as pd
from hypothesis import strategies as st
from factory_clientes import cliente_valido, cliente_con_relacion_invalida
#aca van las estrategias relacionadas con dominio
clientes_validos = cliente_valido()
clientes_invalidos = cliente_con_relacion_invalida()
#ahora, las relacionadas con el dataframe
@st.composite
def df_valido(draw):

    payload = draw(clientes_validos)

    return pd.DataFrame([payload])

@st.composite
def df_invalido(draw):
    payload = draw(clientes_invalidos)
    return pd.DataFrame([payload])

@st.composite
def df_con_indice(draw):
    payload = draw(clientes_validos)
    return pd.DataFrame(
        [payload], index =['indice_valido']
    )

@st.composite
def df_mixto(draw):
    valido = draw(clientes_validos)
    invalido = draw(clientes_invalidos)
    return pd.DataFrame([valido, invalido], index=['indice_valido', 'indice_invalido'])