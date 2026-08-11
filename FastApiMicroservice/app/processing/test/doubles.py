
"""
dobles de test para el validador
"""
import pandas as pd
 
 
class ValidadorFake:
    """Deja pasar el DataFrame sin cambios y registra si lo llamaron."""
 
    def __init__(self):
        self.llamado = False
        self.df_recibido = None
 
    def validar(self, df: pd.DataFrame) -> pd.DataFrame:
        self.llamado = True
        self.df_recibido = df
        return df
    
 
 
class ValidadorQueFalla:
    """Simula un validador que rechaza el input."""
 
    def __init__(self, mensaje: str = "dato invalido"):
        self.mensaje = mensaje
 
    def validar(self, df: pd.DataFrame) -> pd.DataFrame:
        raise ValueError(self.mensaje)