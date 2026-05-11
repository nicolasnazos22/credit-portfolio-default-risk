from pathlib import Path
import numpy as np
from hypothesis import strategies as st
from hypothesis.strategies import composite
PATH_YAML = Path(__file__).resolve().parent.parent / "app" / "reglas_validacion.yaml.txt"
with open(PATH_YAML) as f:
    REGLAS = yaml.safe_load(f)["fields"]


def estrategia_categorica(reglas):
    return st.sampled_from(reglas["valores"])


def estrategia_numerica(reglas, payload):
    min_val = reglas.get("min", 0)
    max_val = reglas.get("max", min_val + 100)
    
    if "mayor" in reglas:
        min_val = reglas["mayor"] + 1
        
    relacion = reglas.get("relation")
    if relacion:
        campo_base = relacion["field"]
        offset = relacion.get("offset", 0)
        max_val = min(max_val, payload[campo_base] + offset)
        
    if reglas.get("dtype") == "float":
        return st.floats(
            min_value=float(min_val),
            max_value=float(max(min_val, max_val)),
            allow_nan=False,
            allow_infinity=False
        )
        
    return st.integers(
        min_value=int(min_val),
        max_value=int(max(min_val, max_val))
    )


def estrategia_para_campo(reglas, payload):
    if reglas.get("categorico"):
        estrategia_base = estrategia_categorica(reglas)
    else:
        estrategia_base = estrategia_numerica(reglas, payload)
        
    if not reglas.get("required", True):
        return st.one_of(st.just(np.nan), estrategia_base)
        
    return estrategia_base


@composite
def cliente_valido(draw):
    payload = {}
    for campo, reglas in REGLAS.items(): #primero genero los valores de campos que no dependen de otros. 
        if not reglas.get("relation"):
            payload[campo] = draw(estrategia_para_campo(reglas, payload))
    for campo, reglas in REGLAS.items():
        if reglas.get("relation"): #una vez generados procedo con los que tienen dependencia. Modelando este problema de dependencias como un grafo aciclico o DAG 
        #la generacion de valores va a estar completamente desacoplada del orden de los campos del YAML, es decir de las reglas de negocio. Es decir instancio primero los que tienen in degree = 0
        #despues los que tienen in degree = 1
            payload[campo] = draw(estrategia_para_campo(reglas, payload)) #aclaracion: estoy asumiendo que el arbol de dependencias tiene maximo 1 nodo hijo
            
    return payload


@composite
def cliente_con_relacion_invalida(draw):
    payload = draw(cliente_valido())
    
    campos_relacionales = [
        campo
        for campo, reglas in REGLAS.items()
        if reglas.get("relation")
    ]
    
    campo = draw(st.sampled_from(campos_relacionales))
    reglas = REGLAS[campo]
    relacion = reglas["relation"]
    campo_base = relacion["field"]
    offset = relacion.get("offset", 0)
    min_invalido = payload[campo_base] + offset + 1
    max_val = reglas.get("max", min_invalido + 100)
    
    if reglas.get("dtype") == "float":
        payload[campo] = draw(
            st.floats(
                min_value=float(min_invalido),
                max_value=float(max_val + 50),
                allow_nan=False,
                allow_infinity=False
            )
        )
    else:
        payload[campo] = draw(
            st.integers(
                min_value=int(min_invalido),
                max_value=int(max_val + 50)
            )
        )
        
    return payload