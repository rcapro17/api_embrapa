import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import BaseConfig

# ----------------------------------------------------------------
# 1) Pegamos a URL do banco de dados diretamente da config (variável de ambiente).
#    Se rodar fora de Docker e não houver DATABASE_URL, cai em SQLite local.
# ----------------------------------------------------------------
DATABASE_URL = BaseConfig.SQLALCHEMY_DATABASE_URI

# Se for SQLite (prefixo "sqlite:///"), habilitamos connect_args; senão, omitimos.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# Cria sessão padrão (bind = engine). Desabilitamos autoflush/​autocommit manual
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db():
    """
    Cria todas as tabelas definidas pelas subclasses de Base (se ainda não existirem).
    Deve ser chamado uma única vez (por exemplo, na inicialização da aplicação).
    """
    Base.metadata.create_all(bind=engine)


def get_engine():
    """
    Retorna o objeto SQLAlchemy Engine. Usado em testes ou introspecção.
    """
    return engine


def get_session():
    """
    Retorna uma nova instância de SessionLocal().
    Use sempre dentro de um contexto try/finally ou com `with` para fechar adequadamente.
    """
    return SessionLocal()
