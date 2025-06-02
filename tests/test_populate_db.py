# tests/test_populate_db.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database import Base, get_engine, get_session
from models.cultivar import Cultivar

# apenas “salvar”, pois testamos inserção direta de Produção
from scripts.populate_db import salvar

from services.scraper import get_producao_data


@pytest.fixture(scope="function")
def test_session(tmp_path):
    """
    Cria um banco SQLite temporário em memória (ou em arquivo temporário) para cada teste.
    """
    # Opcional: usar file físico em tmp_path / "test_embrapa.db"
    db_file = tmp_path / "test_embrapa.db"
    engine = create_engine(
        f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)

    # Cria as tabelas no banco
    Base.metadata.create_all(bind=engine)

    session = Session()
    yield session
    session.close()

    # Apaga o arquivo (caso tenha sido criado)
    if db_file.exists():
        db_file.unlink()


def test_popular_banco_insere_dados(test_session):
    """
    Chamamos 'salvar' passando apenas os dados de Produção (lista de dicionários).
    Verificamos que algo foi inserido.
    """
    # No início, não há registros
    assert test_session.query(Cultivar).count() == 0

    # Faz a inserção dos itens vindos de get_producao_data()
    dados = get_producao_data()
    salvar(dados, test_session)

    total = test_session.query(Cultivar).count()
    assert total > 0, "Esperava ao menos um registro após salvar(get_producao_data())."


def test_popular_banco_nao_reinsere_dados(test_session):
    """
    Salvamos os dados de Produção duas vezes e garantimos que não hajam duplicatas:
    o número de registros após a segunda chamada deve ser igual ao da primeira.
    """
    dados = get_producao_data()

    salvar(dados, test_session)
    count_after_first = test_session.query(Cultivar).count()

    salvar(dados, test_session)
    count_after_second = test_session.query(Cultivar).count()

    assert count_after_second == count_after_first, "Não deveria inserir duplicatas."
