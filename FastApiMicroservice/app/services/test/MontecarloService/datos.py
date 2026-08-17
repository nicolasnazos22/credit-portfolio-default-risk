from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class portfolioEscenario:
    probabilidades: list[float]
    escenarios: int

@dataclass(frozen=True)
class ParMonotonico:
    matriz_random: np.ndarray
    p_bajo: list[float]
    p_alto: list[float]
    @property
    def escenarios(self) -> int:
        return self.matriz_random.shape[0]