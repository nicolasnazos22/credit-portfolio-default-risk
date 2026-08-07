import numpy as np
from app.domain.schemasschemas import PortfolioRiskSimulationResponse
class MontecarloService:
    def simular_riesgo_portfolio(self, probabilidades: list[float], cantidad_escenarios: int) -> PortfolioRiskSimulationResponse:
        array_probabilidades = np.array(probabilidades)
        cantidad_prestamos = len(array_probabilidades)
        generacion_aleatoria = np.random.rand(cantidad_escenarios, cantidad_prestamos)
        matriz_defaults = generacion_aleatoria < array_probabilidades
        defaults_por_iteracion = np.sum(matriz_defaults, axis=1)

        var_95 = np.percentile(defaults_por_iteracion, 95)
        peores_iteraciones = defaults_por_iteracion[defaults_por_iteracion >= 95]
        cvar_95 = np.mean(peores_iteraciones) if len(peores_iteraciones) > 0 else 0.0
        return PortfolioRiskSimulationResponse.armar_respuesta(
            simulaciones = cantidad_escenarios,
            var_95 = int(np.round(var_95))
            cvar_95 = int(np.round(cvar_95))
        )
