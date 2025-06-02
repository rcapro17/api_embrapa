# app.py
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from flask_cors import CORS
from config import DevelopmentConfig  # ou ProductionConfig dependendo do ENV
from routes.auth import auth_bp
from routes.producao import producao_bp
from routes.processamento import processamento_bp
from routes.comercializacao import comercializacao_bp
from routes.importacao import importacao_bp
from routes.exportacao import exportacao_bp
from flask_swagger_ui import get_swaggerui_blueprint
from scripts.populate_db import popular_banco
from models.database import init_db

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)  # ou ProductionConfig

# configurações de CORS usando app.config['CORS_ORIGINS']
CORS(app, resources={
     r"/api/*": {"origins": app.config["CORS_ORIGINS"]}}, supports_credentials=True)

# configurações JWT vindas do config.py
jwt = JWTManager(app)

# registra blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(producao_bp,      url_prefix="/api/producao")
app.register_blueprint(processamento_bp, url_prefix="/api/processamento")
app.register_blueprint(comercializacao_bp, url_prefix="/api/comercializacao")
app.register_blueprint(importacao_bp,    url_prefix="/api/importacao")
app.register_blueprint(exportacao_bp,    url_prefix="/api/exportacao")

# swagger
SWAGGER_URL = app.config["SWAGGER_URL"]
API_URL = app.config["API_YAML_PATH"]
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Embrapa API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == "__main__":
    init_db()      # cria tabelas (usando SQLALCHEMY_DATABASE_URI, que agora aponta para Postgres)
    popular_banco()  # popula dados
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
