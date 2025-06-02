# routes/auth.py

from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth_bp = Blueprint("auth", __name__, url_prefix="")


@auth_bp.route("/token", methods=["GET"])
def token():
    """
    Gera um par (access_token, refresh_token). Não requer autenticação.
    """
    access = create_access_token(identity="user")
    refresh = create_refresh_token(identity="user")
    return jsonify({
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "Bearer",
        # opcional: se quiser informar expires_in, pode buscar em app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    })


@auth_bp.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Recebe via cabeçalho um refresh_token válido e emite um novo access_token.
    """
    current = get_jwt_identity()
    new_access = create_access_token(identity=current)
    return jsonify({
        "access_token": new_access
    })
