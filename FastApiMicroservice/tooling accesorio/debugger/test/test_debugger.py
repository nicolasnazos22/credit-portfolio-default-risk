import pytest
from src.debugger_dependencias_yaml import diagnostico_reglas_conflicto
def test_vacio():
    assert diagnostico_reglas_conflicto({}) == []
def test_lineal_sin_ciclo(): #a relacionado con b, b relacionado con c. a -> b -> c
    reglas = {
        "a": {"relation": {"field": "b"}},
        "b": {"relation": {"field": "c"}},
        "c": {}
    }
    assert diagnostico_reglas_conflicto(reglas) == []

def test_dos_cadenas(): #2 componentes conexas a -> b c -> d
    reglas = {
        "a": {"relation": {"field": "b"}},
        "b": {},
        "c": {"relation": {"field": "d"}},
        "d": {}
    }
    assert diagnostico_reglas_conflicto(reglas) == []


def test_dependencia_circular_simple(): #por ej: un cliente valido necesita que su experiencia laboral sea su edad biologica - 16 años (edad mínima para trabajar legalmente) y también necesita que 
#su edad biológica  sea experiencia laboral + 16 años
    reglas = {
        "a": {"relation": {"field": "b"}},
        "b": {"relation": {"field": "a"}},
    }
    resultado = diagnostico_reglas_conflicto(reglas)
    assert len(resultado) == 1
    assert set(resultado[0][:-1]) == {"a", "b"}

def test_cadena_dependencias_cerrada(): #
    reglas = {
        "a": {"relation": {"field": "b"}},
        "b": {"relation": {"field": "c"}},
        "c": {"relation": {"field": "a"}},
    }
    resultado = diagnostico_reglas_conflicto(reglas)
    assert len(resultado) == 1
    assert set(resultado[0][:-1]) == {"a", "b", "c"}

def test_solo_dependencias_circulares(): #aca testeamos otra propiedad clave: que solamente se incluya en la traza del error a -> b -> a. d no forma parte del mismo, por diseño debería eliminarse. 
#Ejemplo: longitud de historial crediticio debe ser menor o igual a la edad biológica - 18 años (edad mínima para tomar un crédito)
# edad biologica debe ser experiencia laboral + 16. Experiencia laboral debe ser edad biologica - 16
    reglas = {
        "d": {"relation": {"field": "a"}},
        "a": {"relation": {"field": "b"}},
        "b": {"relation": {"field": "a"}},
    }
    resultado = diagnostico_reglas_conflicto(reglas)
    assert len(resultado) == 1
    assert "d" not in resultado[0]

def test_dos_circulares_independientes():
    reglas = {
        "a": {"relation": {"field": "b"}},
        "b": {"relation": {"field": "a"}},
        "c": {"relation": {"field": "d"}},
        "d": {"relation": {"field": "c"}},
    }
    resultado = diagnostico_reglas_conflicto(reglas)
    assert len(resultado) == 2

