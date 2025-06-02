# scripts/populate_db.py

from services.scraper import (
    get_processamento_data,
    get_producao_data,
    get_comercializacao_data,
    get_importacao_data,
    get_exportacao_data
)
from models.database import SessionLocal, init_db
from models.cultivar import Cultivar
from sqlalchemy import and_


def banco_vazio(session):
    return session.query(Cultivar).first() is None


def salvar(dados, session):
    novos = 0
    ignorados = 0

    for item in dados:
        filtros = []

        # Filtrar por etapa (sempre presente)
        if item.get("etapa") is not None:
            filtros.append(Cultivar.etapa == item["etapa"])

        # Processamento:
        if item.get("categoria_uva") is not None:
            filtros.append(Cultivar.categoria_uva == item["categoria_uva"])
        if item.get("tipo_uva") is not None:
            filtros.append(Cultivar.tipo_uva == item["tipo_uva"])
        if item.get("nome_uva") is not None:
            filtros.append(Cultivar.nome_uva == item["nome_uva"])

        # Produção / Comerc / Imp / Exp:
        if item.get("categoria_produto") is not None:
            filtros.append(Cultivar.categoria_produto ==
                           item["categoria_produto"])
        if item.get("tipo_produto") is not None:
            filtros.append(Cultivar.tipo_produto == item["tipo_produto"])
        if item.get("produto") is not None:
            filtros.append(Cultivar.produto == item["produto"])

        # Quantidade em litros (string) – somente se não estiver vazia:
        if item.get("quantidade_l"):
            filtros.append(Cultivar.quantidade_l == item["quantidade_l"])

        # Quantidade em kg (int) – somente se for int, não None
        qtkg = item.get("quantidade_kg")
        if isinstance(qtkg, int):
            filtros.append(Cultivar.quantidade_kg == qtkg)

        # Valor em USD (int) – somente se for int, não None
        valor_usd = item.get("valor_usd")
        if isinstance(valor_usd, int):
            filtros.append(Cultivar.valor_usd == valor_usd)

        # Ano (sempre inteiro)
        if item.get("ano") is not None:
            filtros.append(Cultivar.ano == item["ano"])

        # País (string) – somente se não for vazio:
        if item.get("pais"):
            filtros.append(Cultivar.pais == item["pais"])

        # Agora verificamos se já existe:
        exists = session.query(Cultivar).filter(and_(*filtros)).first()

        if not exists:
            # Constrói o dicionário “novo_item” exatamente com as chaves que nosso modelo aceita:
            novo_item = {}
            for k, v in item.items():
                # renomeia “quantidade_l” caso usado com barra ou maiúsculas (por segurança):
                if k in ("quantidade/L", "Quantidade/L"):
                    novo_item["quantidade_l"] = v
                else:
                    novo_item[k] = v
            session.add(Cultivar(**novo_item))
            novos += 1
            print(f"✔ Inserido: {novo_item}")
        else:
            ignorados += 1

    print(
        f"\nResumo: {novos} inseridos | {ignorados} ignorados (duplicatas)\n")


def popular_banco():
    session = SessionLocal()
    if banco_vazio(session):
        print("📦 Banco vazio. Iniciando inserção de dados da Embrapa...\n")
        salvar(get_producao_data(), session)
        salvar(get_processamento_data(), session)
        salvar(get_comercializacao_data(), session)
        salvar(get_importacao_data(), session)
        salvar(get_exportacao_data(), session)
        print("✅ Dados populados com sucesso.")
    else:
        print("⚠ Banco já possui dados. Nenhuma inserção realizada.")

    session.commit()
    session.close()


if __name__ == "__main__":
    init_db()
    popular_banco()
