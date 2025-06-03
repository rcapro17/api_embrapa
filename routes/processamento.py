# routes/processamento.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from services.scraper import get_processamento_data
from logging_config import logger

processamento_bp = Blueprint(
    "processamento", __name__, url_prefix="/api/processamento"
)


def paginar(dados, limit, offset):
    return dados[offset: offset + limit]


@processamento_bp.route("", methods=["GET"])
@jwt_required()
def listar_processamento():
    """
    Parâmetros opcionais (query string):
      - ano (int)
      - categoria_uva (string)
      - tipo_uva (string)
      - ano_inicio (int, default=2020)
      - ano_fim (int, default=2024)
      - limit (int, default=100)
      - offset (int, default=0)
    """
    try:
        ano_inicio = int(request.args.get("ano_inicio", 1970))
        ano_fim = int(request.args.get("ano_fim", 2024))
        dados = get_processamento_data(ano_inicio=ano_inicio, ano_fim=ano_fim)
    except Exception as e:
        logger.error(f"Erro ao obter dados de processamento: {e}")
        return jsonify({"erro": "Erro interno ao processar os dados"}), 500

    ano_f = request.args.get("ano")
    if ano_f:
        try:
            ano_i = int(ano_f)
            dados = [item for item in dados if item.get("ano") == ano_i]
        except ValueError:
            pass

    cat_uva = request.args.get("categoria_uva")
    if cat_uva:
        dados = [item for item in dados if item.get(
            "categoria_uva") == cat_uva]

    tipo_f = request.args.get("tipo_uva")
    if tipo_f:
        dados = [item for item in dados if item.get("tipo_uva") == tipo_f]

    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    return jsonify(paginar(dados, limit, offset))
