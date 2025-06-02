# scripts/verificar_dados.py

from sqlalchemy import func
from models.database import SessionLocal
from models.cultivar import Cultivar


def verificar_registros():
    session = SessionLocal()

    total = session.query(Cultivar).count()
    por_etapa = session.query(
        Cultivar.etapa, func.count()).group_by(Cultivar.etapa).all()
    anos = session.query(Cultivar.ano).distinct().order_by(Cultivar.ano).all()
    cats_prod = session.query(Cultivar.categoria_produto).distinct().all()
    cats_uva = session.query(Cultivar.categoria_uva).distinct().all()

    print(f"\n🔍 Total de registros: {total}")
    print("\n📊 Registros por etapa:")
    for etapa, count in por_etapa:
        print(f"  - {etapa}: {count}")

    print("\n📆 Anos encontrados:")
    for (ano,) in anos:
        print(f"  - {ano}")

    print("\n🏷️ Categorias de produto:")
    for (cat,) in cats_prod:
        if cat is not None:
            print(f"  - {cat}")

    print("\n🏷️ Categorias de uva:")
    for (cat,) in cats_uva:
        if cat is not None:
            print(f"  - {cat}")

    session.close()


if __name__ == "__main__":
    verificar_registros()
