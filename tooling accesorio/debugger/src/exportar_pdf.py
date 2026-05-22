import textwrap
from datetime import datetime
from fpdf import FPDF

def exportar_reporte_a_pdf(texto_reporte: str, ruta_salida: str = "reporte_dependencias_circulares.pdf"):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Reporte de validación YAML", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", size=10)
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 8, f"Fecha de validación: {fecha}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    texto_limpio = texto_reporte.replace('\t', '    ')

    for linea in texto_limpio.splitlines():
        linea = linea.strip()

        if not linea:
            pdf.ln(2)
            continue

        estilo = "B" if linea.startswith("Conflicto #") else ""
        pdf.set_font("helvetica", style=estilo, size=11)
    
        tramos = textwrap.wrap(linea, width=90, break_long_words=True)
        
        for tramo in tramos:
            pdf.cell(0, 6, txt=tramo, new_x="LMARGIN", new_y="NEXT") 

    pdf.output(ruta_salida)