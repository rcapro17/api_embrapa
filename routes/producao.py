# routes/producao.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from services.scraper import get_producao_data
from logging_config import logger

producao_bp = Blueprint("producao", __name__, url_prefix="/api/producao")


def paginar(dados, limit, offset):
    return dados[offset: offset + limit]


@producao_bp.route("", methods=["GET"])
@jwt_required()
def listar_producao():
    """
    Parâmetros opcionais (query string):
      - ano (int)
      - categoria_produto (string)
      - tipo_produto (string)
      - ano_inicio (int, default=2020)
      - ano_fim (int, default=2024)
      - limit (int, default=100)
      - offset (int, default=0)
    """
    try:
        ano_inicio = int(request.args.get("ano_inicio", 1970))
        ano_fim = int(request.args.get("ano_fim", 2024))
        dados = get_producao_data(ano_inicio=ano_inicio, ano_fim=ano_fim)
    except Exception as e:
        logger.error(f"Erro ao obter dados de produção: {e}")
        return jsonify({"erro": "Erro interno ao processar os dados"}), 500

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

    tipo = request.args.get("tipo_produto")
    if tipo:
        dados = [item for item in dados if item.get("tipo_produto") == tipo]

    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    return jsonify(paginar(dados, limit, offset))
