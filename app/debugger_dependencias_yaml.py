from typing import Optional

def diagnostico_reglas_conflicto(reglas: dict) -> Optional[str]:
    dependencias_campos = {
        campo: [] for campo in reglas
    }
    
    for campo, configuracion in reglas.items():
        relacion = configuracion.get("relation") 
        if relacion:
            dependencias_campos[campo].append(relacion["field"])

    campos_visitados = set()
    campos_en_proceso = set()
    dependencias_cadena = []
    
    reglas_conflictivas_detectadas = []

    def rastreo_reglas_conflicto(campo_actual):
        campos_visitados.add(campo_actual)
        campos_en_proceso.add(campo_actual)
        dependencias_cadena.append(campo_actual)

        for campo_requerido in dependencias_campos[campo_actual]:
            if campo_requerido not in campos_visitados: 
                rastreo_reglas_conflicto(campo_requerido) #este es el paso recursivo del dfs, si no lo visite visito sus vecinos
                
            elif campo_requerido in campos_en_proceso: #aca detecte una backedge, es decir una dependencia circular
                indice_inicio_dependencia_circular = dependencias_cadena.index(campo_requerido) #reconstruyo exactamente la dependencia circular detectada, obviando los campos previos.
                ciclo_dependencia_circular = dependencias_cadena[indice_inicio_dependencia_circular:] + [campo_requerido] #concateno campo o campos que forman el ciclo 
                
                if ciclo_dependencia_circular not in reglas_conflictivas_detectadas: 
                    reglas_conflictivas_detectadas.append(ciclo_dependencia_circular)
        
        campos_en_proceso.remove(campo_actual) #aca saco el campo actual del stack de resolución y sigo explorando las dependencias de ese campo.
        dependencias_cadena.pop()

    # Aca exploro todos los campos. El DFS explora básicamente las dependencias conectadas a un solo campo (lo que se conoce como componente conexa en teoría de grafos), de esta manera recorro el espacio muestral de campos completos. 
    # En lenguaje financiero: acá garantizo que las relaciones de todos los campos sean exploradas
    for campo in dependencias_campos:
        if campo not in campos_visitados:
            rastreo_reglas_conflicto(campo)

    if not reglas_conflictivas_detectadas:
        return None



