# Embrapa Vitiviniculture Data API

## 🍇 Visão Geral

Esta é uma REST API desenvolvida em **Python (Flask)** que automatiza a coleta, organização e exposição dos dados históricos de **vitivinicultura no Brasil** a partir do site da **EMBRAPA**. Ela permite o acesso estruturado a informações de:

- 🌾 **Produção**
- 🍶 **Processamento de uvas**
- 🍾 **Comercialização de produtos vitivinícolas**
- 🌿 **Importação de derivados**
- 🌎 **Exportação de derivados**

Esta API é projetada para ser **pública, documentada, e segura**, com autenticação JWT.

## 🤖 Objetivo do Projeto

Esta API faz parte de um pipeline de dados que visa abastecer modelos de **Machine Learning voltados ao mercado financeiro**. Especificamente, **fintechs e bancos de análise de risco** poderão usar as séries históricas da vitivinicultura para:

- Analisar **potencial de financiamento** da cadeia do vinho e da uva
- Avaliar **sazonalidade e produtividade** regional
- Antecipar **riscos e oportunidades** agrícolas
- Criar **produtos financeiros especializados** (crédito rural, seguros, hedge, etc.)

---

## 🚀 Tecnologias Usadas

- `Python 3.11`
- `Flask` com `Blueprints`
- `Flask-JWT-Extended`
- `BeautifulSoup4` para scraping
- `pytest` + `coverage`
- `Docker` + `DockerHub`
- `Render` (Deploy)
- `PostgreSQL` (Render Cloud DB)
- `GitHub Actions` (CI/CD)

---

## 📁 Estrutura de Pastas

```
api_embrapa/
├── app.py
├── services/
│   └── scraper.py
├── routes/
│   ├── producao.py
│   ├── processamento.py
│   ├── comercializacao.py
│   ├── importacao.py
│   └── exportacao.py
├── scripts/
│   └── populate_db.py
├── models/
├── tests/
├── Dockerfile
├── requirements.txt
├── logging_config.py
└── README.md
```

---

## 🌐 Arquitetura do Projeto

```
Desenvolvedor (GitHub)
     └── Push para repo
           ⇓
     GitHub Actions (CI/CD)
        └── Executa testes + build Docker
                ⇓
        DockerHub (rca17/api_embrapa)
                ⇓
            Render.com
      ├─ Web Service (Flask)
      └─ PostgreSQL (dados persistidos)
                ⇓
     Front-end ou Cliente (GET com filtros)
```

### 🔄 Tecnicamente:

- Cada rota acessa uma função no `scraper.py` que faz scraping dinâmico da EMBRAPA
- Os dados podem ser paginados e filtrados por query strings
- Logs são centralizados no `logging_config.py`
- Banco no Render com pooling
- Deploy automatizado via Docker e CI/CD (GitHub Actions)

---

## 📚 Como Rodar Localmente

### 1. Clone o repositório

```bash
git clone https://github.com/rcapro17/api_embrapa.git
cd api_embrapa
```

### 2. Crie o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente

Crie um arquivo `.env` (ou exporte diretamente):

```env
DATABASE_URL=postgresql://... (se local)
JWT_SECRET_KEY=sua-chave-secreta
```

### 5. Rode a API

```bash
flask run
```

### 6. Teste

```bash
pytest --maxfail=1 --disable-warnings -v
```

---

## 🛡️ Autenticação JWT

As rotas da API são protegidas com JWT.

1. Faça login com credenciais test (ou cadastre no futuro)
2. Receba `access_token` e `refresh_token`
3. Use `Authorization: Bearer <access_token>` nas chamadas

---

## 🤖 Exemplo de Uso

```bash
curl -H "Authorization: Bearer <token>" \
  "https://api-emb-prd.onrender.com/api/processamento?ano=2022&categoria_uva=Viníferas&limit=10"
```

Resposta:

```json
[
  {
    "ano": 2022,
    "categoria_uva": "Viníferas",
    "tipo_uva": "Tintas",
    "nome_uva": "Cabernet Sauvignon",
    "quantidade_kg": 2837264,
    "etapa": "Processamento"
  },
  ...
]
```

---

## 🧠 Possível Uso com Machine Learning

Com os dados coletados da API, é possível alimentar modelos que:

- 🤷️ Preveem safra ou volume de exportação
- 🤝 Analisam impacto de importação em preço de mercado
- 📊 Segmentam oportunidades de crédito por tipo de uva ou região
- 🏛️ Alimentam dashboards de decisão financeira para agrofintechs

---

## 🌟 Status do Projeto

- [x] Scraper completo com logs
- [x] API REST com filtros, paginação e autenticação
- [x] Testes unitários com `pytest`
- [x] Dockerfile pronto para CI/CD
- [x] Deploy com link público via Render

---

## 🌟 Contribuição

Pull requests são bem-vindos. Para mudanças significativas, abra uma issue antes.

---

## 👉 Autor

Desenvolvido por Rodrigo Cunha | [LinkedIn](https://linkedin.com/in/seunome) | [GitHub](https://github.com/seuusuario)
