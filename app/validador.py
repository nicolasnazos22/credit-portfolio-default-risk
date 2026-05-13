import pandas as pd
import numpy as np

# reglas de validacion codificadas en dispatch table
# para evitar branching innecesario

REGLAS_VALIDACION_INDIVIDUAL = {
    "min": lambda clientes, feature, valor: clientes[feature] >= valor,
    "max": lambda clientes, feature, valor: clientes[feature] <= valor,
    "mayor": lambda clientes, feature, valor: clientes[feature] > valor,
    "menor": lambda clientes, feature, valor: clientes[feature] < valor,
}


REGLAS_VALIDACION_RELACIONES = {
    "menor_o_igual": lambda clientes, feature, relacion: clientes[feature] <= (clientes[relacion["field"]] + relacion.get("offset", 0)),
}


class Validador:

    def __init__(self, atributos: dict):
        self.atributos = atributos["fields"]

    def validar(self, clientes: pd.DataFrame) -> pd.DataFrame:

        features_requeridas = [
            feature
            for feature, validaciones in self.atributos.items()
            if validaciones.get("required")
        ]

        clientes = clientes.dropna(subset=features_requeridas)

        condiciones_validacion = [
            condicion_validacion
            for feature, validaciones in self.atributos.items()
            if feature in clientes.columns
            for condicion_validacion in self._construir_condiciones_validacion(clientes, feature, validaciones)
        ]

        if condiciones_validacion:
            clientes = clientes[np.logical_and.reduce(condiciones_validacion)]

        if clientes.empty:
            raise ValueError("No hay clientes validos tras la validacion.")

        return clientes.copy()

    def _construir_condiciones_validacion(self, clientes: pd.DataFrame, feature: str, validaciones: dict) -> list[pd.Series]:

        condiciones_individuales = [
            funcion_validacion(clientes, feature, validaciones[tipo_validacion])
            for tipo_validacion, funcion_validacion in REGLAS_VALIDACION_INDIVIDUAL.items()
            if tipo_validacion in validaciones
        ]

        condiciones_relacionales = [
            REGLAS_VALIDACION_RELACIONES[relacion["type"]](clientes, feature, relacion)
            for relacion in [validaciones.get("relation")]
            if relacion
        ]

        return condiciones_individuales + condiciones_relacionales