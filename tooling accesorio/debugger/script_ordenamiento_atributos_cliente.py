import yaml
from pathlib import Path
from graphlib import TopologicalSorter, CycleError

PATH_YAML = Path(__file__).resolve().parent.parent / "app" / "reglas_validacion.yaml.txt"

with open(PATH_YAML) as f:
    REGLAS = yaml.safe_load(f)["fields"]


# Aca está la magia: con 2 líneas de código, sin lógica compleja, valido las reglas de negocio codificadas en el YAML por el analista funcional y lo obligo a revisarlas en caso de haber problemas.
def obtener_orden_instanciacion(reglas_dict):
    sorter = TopologicalSorter()

    for campo, reglas in reglas_dict.items():
        relacion = reglas.get("relation")

        if relacion:
            sorter.add(campo, relacion["field"])
        else:
            sorter.add(campo)

    try:
        # Ejemplo:
        # ['edad', 'ingresos', 'cuota']
        return list(sorter.static_order())

    except CycleError:
        raise ValueError(
            "Dependencia circular detectada en el YAML."
        )


# 3. Cacheamos el orden global de resolución
ORDEN_CAMPOS = obtener_orden_instanciacion(REGLAS)