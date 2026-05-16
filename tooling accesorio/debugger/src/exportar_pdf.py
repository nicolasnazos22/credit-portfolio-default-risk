from fpdf import FPDF
from datetime import datetime

def exportar_reporte_a_pdf(
    texto_reporte: str,
    ruta_salida: str = "reporte_dependencias_circulares.pdf"
):
    pdf = FPDF()
    pdf.add_page()
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Reporte de validacion YAML", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("helvetica", size=10)
    pdf.cell(0, 8, f"fecha de validacion: {fecha_actual}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    for linea in texto_reporte.split("\n"):
        if linea.startswith("Conflicto #"):
            pdf.set_font("helvetica", "B", 11)
        else:
            pdf.set_font("helvetica", size=11)
        pdf.multi_cell(0, 6, linea)

    pdf.output(ruta_salida)