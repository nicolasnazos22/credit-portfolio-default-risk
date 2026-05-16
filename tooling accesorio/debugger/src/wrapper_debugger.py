import sys
from debuggear_dependencias_yaml import diagnostico_reglas_conflicto
from formateador_reporte import formatear_reporte
from exportar_pdf import exportar_reporte_a_pdf
import yaml
"""
script wrapper cli para generar reporte de dependencias circulares para analista
"""
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python wrapper.py archivo.yaml")
        sys.exit(1)

    nombre_yaml = sys.argv[1]

    with open(nombre_yaml, "r", encoding="utf-8") as f:
        reglas_negocio = yaml.safe_load(f)
    #primero corro el debugger
    reglas_debuggeadas = diagnostico_reglas_conflicto(reglas_negocio) or []
    if reglas_debuggeadas == []:
        print("todo ok, no hay conflictos detectados")
        exit(0)
    
    reglas_formateadas = formatear_reporte(reglas_debuggeadas)
    exportar_reporte_a_pdf(reglas_formateadas)