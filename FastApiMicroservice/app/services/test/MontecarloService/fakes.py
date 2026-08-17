import numpy as np

class FakeRng:
    """RNG determinista que devuelve una matriz controlada."""

    def __init__(self, matriz):
        self._matriz = np.asarray(matriz)

    def random(self, shape):
        if shape != self._matriz.shape:
            raise AssertionError(
                f"shape esperado {self._matriz.shape}, "
                f"pedido {shape}"
            )

        return self._matriz.copy()