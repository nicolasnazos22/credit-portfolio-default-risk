import pytest

from src.formateador_reporte import formatear_reporte


def test_contenido_reportes():
    conflictos = [["a", "b", "a"], ["c", "d", "c"]]
    reporte = formatear_reporte(conflictos)
    
    assert isinstance(reporte, str)
    assert "Conflicto #1" in reporte
    assert "Conflicto #2" in reporte
