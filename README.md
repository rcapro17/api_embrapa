# Embrapa API com MySQL

API RESTful com Flask, BeautifulSoup, SQLAlchemy e MySQL. JWT incluído sem login.

## Como usar
1. Configure o banco MySQL e atualize o arquivo `models/database.py`
2. Rode `python scripts/populate_db.py` para popular o banco
3. Inicie o servidor com `python app.py`
4. Obtenha um token em `/token`
5. Use o token nas rotas `/api/...`
