import pandas as pd
from hypothesis import strategies as st
from factory_clientes import cliente_valido, cliente_con_relacion_invalida
#aca van las estrategias relacionadas con dominio
clientes_validos = cliente_valido()
clientes_invalidos = cliente_con_relacion_invalida()
lista_clientes_validos = st.lists(clientes_validos, min_size=2, max_size=20)
lista_clientes_invalidos = st.lists(clientes_invalidos, min_size=1, max_size=10)
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

@st.composite
def df_lista_validos(draw):
    payload_validos = draw(lista_clientes_validos)
    return pd.DataFrame(payload_validos)

@st.composite
def df_lista_mixta(draw):
    payloads_validos = draw(lista_clientes_validos)
    payloads_invalidos = draw(lista_clientes_invalidos)
    dataframe_validos_indexados = pd.DataFrame(payloads_validos, index=[f"valido_{indice}" for indice in range(len(payloads_validos))])
    dataframe_invalidos_indexados = pd.DataFrame(payloads_invalidos, index=[f"invalido_{indice}" for indice in range(len(payloads_invalidos))])
    return pd.concat([dataframe_validos_indexados, dataframe_invalidos_indexados])



