import pytest

from src.formateador_reporte import formatear_reporte


def test_contenido_reportes():
    conflictos = [["a", "b", "a"], ["c", "d", "c"]]
    reporte = formatear_reporte(conflictos)
    campos = ["a", "b", "c", "d"]
    
    assert isinstance(reporte, str)
    assert reporte.count("Conflicto ") == 2
    assert all(campo in reporte for campo in campos)
