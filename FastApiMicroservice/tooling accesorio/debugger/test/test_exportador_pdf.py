from pathlib import Path

from src.exportar_pdf import exportar_reporte_a_pdf


def test_exporta_pdf(tmp_path):

    ruta_guardado = tmp_path / "reporte.pdf"

    exportar_reporte_a_pdf(
        texto_a_escribir="conflicto de prueba",
        ruta_guardado=str(ruta_guardado)
    )

    assert ruta_guardado.exists() #este assert asegura que el archivo es creado exitosamente.
    assert ruta_guardado.stat().st_size > 0 #aca me aseguro de que el contenido sea escrito.