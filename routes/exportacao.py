# routes/exportacao.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from services.scraper import get_exportacao_data

exportacao_bp = Blueprint("exportacao", __name__, url_prefix="/api/exportacao")


def paginar(dados, limit, offset):
    return dados[offset: offset + limit]


@exportacao_bp.route("", methods=["GET"])
@jwt_required()
def listar_exportacao():
    """
    Parâmetros opcionais (query string):
      - ano (int)
      - categoria_produto (string)
      - pais (string)
      - limit (int, default=100)
      - offset (int, default=0)
    """
    dados = get_exportacao_data()
    ano_f = request.args.get("ano")
    if ano_f:
        try:
            ano_i = int(ano_f)
            dados = [item for item in dados if item.get("ano") == ano_i]
        except ValueError:
            pass

    cat_prod = request.args.get("categoria_produto")
    if cat_prod:
        dados = [item for item in dados if item.get(
            "categoria_produto") == cat_prod]

    pais_f = request.args.get("pais")
    if pais_f:
        dados = [item for item in dados if item.get("pais") == pais_f]

    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    return jsonify(paginar(dados, limit, offset))
