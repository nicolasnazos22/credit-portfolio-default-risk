def formatear_reporte(conflictos: list) -> str:
    documento = [
      "Las siguientes reglas necesitan definición clara. Por favor revisar el archivo .YAML"
    ]

    for nro_conflicto, conflicto in enumerate(conflictos, start=1):
        documento.append(f"Conflicto #{nro_conflicto}:")
        for nro_dependencia in range(len(conflicto) - 1):
            documento.append(
                f"  - '{conflicto[nro_dependencia]}' depende de' {conflicto[nro_dependencia + 1]}'."
            )
        documento.append("")

    return "\n".join(documento)