from sqlalchemy import Column, Integer, String, UniqueConstraint
from models.database import Base


class Cultivar(Base):
    __tablename__ = "cultivares"

    id = Column(Integer, primary_key=True, index=True)
    etapa = Column(String(50), nullable=False, index=True)
    categoria_uva = Column(String(100), nullable=True, index=True)
    tipo_uva = Column(String(100), nullable=True, index=True)
    nome_uva = Column(String(100), nullable=True)
    categoria_produto = Column(String(100), nullable=True, index=True)
    tipo_produto = Column(String(100), nullable=True)
    produto = Column(String(100), nullable=True)
    quantidade_l = Column(String(50),  nullable=True)
    quantidade_kg = Column(Integer,   nullable=True)
    valor_usd = Column(Integer, nullable=True)
    ano = Column(Integer, nullable=False, index=True)
    pais = Column(String(100), nullable=True, index=True)

    __table_args__ = (
        UniqueConstraint(
            "etapa",
            "ano",
            "categoria_uva",
            "tipo_uva",
            "nome_uva",
            "categoria_produto",
            "tipo_produto",
            "produto",
            "quantidade_l",
            "quantidade_kg",
            "valor_usd",
            "pais",
            name="uix_cultivar_unico"
        ),
    )

    def to_dict(self):
        """
        Convert object em dicionário simples, para JSON serialização.
        """
        return {
            "id": self.id,
            "etapa": self.etapa,
            "categoria_uva": self.categoria_uva,
            "tipo_uva": self.tipo_uva,
            "nome_uva": self.nome_uva,
            "categoria_produto": self.categoria_produto,
            "tipo_produto": self.tipo_produto,
            "produto": self.produto,
            "quantidade_l": self.quantidade_l,
            "quantidade_kg": self.quantidade_kg,
            "valor_usd": self.valor_usd,
            "ano": self.ano,
            "pais": self.pais,
        }
