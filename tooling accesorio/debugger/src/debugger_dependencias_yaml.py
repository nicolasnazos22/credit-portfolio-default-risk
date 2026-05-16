from typing import Optional

def diagnostico_reglas_conflicto(reglas: dict) -> Optional[list]:
    dependencias_campos = {
        campo: [] for campo in reglas
    }
    
    for campo, configuracion in reglas.items():
        relacion = configuracion.get("relation") 
        if relacion:
            dependencias_campos[campo].append(relacion["field"]) #armo grafo usando diccionario+listas de adyacencia para modelar relaciones.
            if relacion["field"] not in dependencias_campos:
                dependencias_campos[relacion["field"]] = [] 

    campos_visitados = set()
    campos_en_proceso = set()
    dependencias_cadena = []
    diccionario_posiciones = {}
    
    reglas_conflictivas_detectadas = []
    def eliminar_conflictos_repetidos(conflictos: list) -> list:
        if not conflictos: return []
        conflicto_sin_repetidos = set() 
        conflictos_totales = []
        for conflicto in conflictos:
            camino_normalizado = conflicto[:-1] if conflicto[-1] == conflicto[0] else conflicto
            indice_primer_conflicto = camino_normalizado.index(min(camino_normalizado))
            normalizacion = tuple(camino_normalizado[indice_primer_conflicto:] + camino_normalizado[:indice_primer_conflicto])
            if normalizacion not in conflicto_sin_repetidos:
                conflicto_sin_repetidos.add(normalizacion)
                conflictos_totales.append(list(normalizacion) + [normalizacion[0]])
        return conflictos_totales

    def rastreo_reglas_conflicto(campo_actual):
        campos_visitados.add(campo_actual)
        campos_en_proceso.add(campo_actual)
        diccionario_posiciones[campo_actual] = len(dependencias_cadena)
        dependencias_cadena.append(campo_actual)
        for campo_requerido in dependencias_campos[campo_actual]:
            if campo_requerido not in campos_visitados: 
                rastreo_reglas_conflicto(campo_requerido) #este es el paso recursivo del dfs, si no lo visite visito sus vecinos
                
            elif campo_requerido in campos_en_proceso: #aca detecte una backedge, es decir una dependencia circular
                inicio_ciclo = diccionario_posiciones[campo_requerido]
                ciclo_dependencia_circular = (dependencias_cadena[inicio_ciclo:] + [campo_requerido]
)
                if ciclo_dependencia_circular not in reglas_conflictivas_detectadas: 
                    reglas_conflictivas_detectadas.append(ciclo_dependencia_circular)
        
        campos_en_proceso.remove(campo_actual) #aca saco el campo actual del stack de resolución y sigo explorando las dependencias de ese campo.
        dependencias_cadena.pop()
        diccionario_posiciones.pop(campo_actual)

    # Aca corro DFS sobre todos los campos para cubrir todas las componentes no conexas del grafo.
    for campo in dependencias_campos:
        if campo not in campos_visitados:
            rastreo_reglas_conflicto(campo)
    conflictos_sin_repetir =  eliminar_conflictos_repetidos(reglas_conflictivas_detectadas) 
    if not reglas_conflictivas_detectadas:
        return None
    return conflictos_sin_repetir



