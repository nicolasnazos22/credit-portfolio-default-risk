"""
fixtures compartidas
"""
import pandas as pd
import pytest

from app.core.config import ProcessingConfig
from doubles import ValidadorFake


@pytest.fixture
def medianas():
    return pd.Series({"edad": 35.0, "ingreso": 50000.0, "score": 650.0})


@pytest.fixture
def config():
    #cuando pytest pida config se entrega una instancia real de processingconfig
    return ProcessingConfig()


@pytest.fixture
def validador_ok():
    return ValidadorFake()
"""
como busco testear el preprocesador y no el validador uso la instancia de validador más laxa posible,
para enfocarme de lleno en testear el comportamiento del preprocesador
"""