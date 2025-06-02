# tests/test_verificacao_dados.py

import os
import pytest
from sqlalchemy import func
from models.database import SessionLocal, init_db
from models.cultivar import Cultivar

from scripts.populate_db import popular_banco


@pytest.fixture(scope="module", autouse=True)
def preparar_banco():
    """
    Antes de qualquer teste deste módulo:
    - Remove o embrapa.db antigo (se existir)
    - Cria o esquema via init_db()
    - Popula chamando popular_banco()
    Ao final do módulo, remove o embrapa.db novamente.
    """
    # 1) Apaga banco antigo, se existir
    try:
        if os.path.exists("embrapa.db"):
            os.remove("embrapa.db")
    except Exception:
        pass

    # 2) Cria o esquema e popula
    init_db()
    popular_banco()

    yield

    # 3) Ao final do módulo, apagar para não "poluir" o diretório
    try:
        if os.path.exists("embrapa.db"):
            os.remove("embrapa.db")
    except Exception:
        pass


@pytest.fixture
def session():
    db = SessionLocal()
    yield db
    db.close()


def test_cultivar_table_has_data(session):
    total = session.query(Cultivar).count()
    assert total > 0, "Tabela 'cultivares' deve conter pelo menos um registro"


def test_cultivar_has_multiple_etapas(session):
    etapas = session.query(Cultivar.etapa).distinct().all()
    assert len(
        etapas) > 1, "Deve haver mais de uma etapa (Produção, Processamento, etc.)"


def test_cultivar_has_anos(session):
    anos = session.query(Cultivar.ano).distinct().all()
    assert len(anos) > 0, "Nenhum ano encontrado nos registros"


def test_cultivar_has_categorias_produto(session):
    categorias = session.query(Cultivar.categoria_produto).distinct().all()
    # Pelo menos uma dessas categorias deve ser não-None
    assert any(cat[0] is not None for cat in categorias), \
        "Nenhuma categoria_produto válida encontrada"


def test_cultivar_has_categorias_uva(session):
    categorias_uva = session.query(Cultivar.categoria_uva).distinct().all()
    # Pode ser que nem todos os registros tenham categoria_uva (apenas Processamento),
    # mas deve haver ao menos uma categoria_uva não-None
    assert any(cat[0] is not None for cat in categorias_uva), \
        "Nenhuma categoria_uva válida encontrada"
