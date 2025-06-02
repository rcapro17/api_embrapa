# services/scraper.py

import requests
from bs4 import BeautifulSoup

# -------------------------------------------------------------------
# =============< CONFIGURAÇÕES GERAIS >===============================
# -------------------------------------------------------------------

# Timeout padrão em segundos para cada requisição HTTP
REQUEST_TIMEOUT = 10

# Cabeçalhos HTTP padrão (pode incluir autenticação ou User‐Agent customizado)
HTTP_HEADERS = {
    "User-Agent": "Embrapa-Data-Scraper/1.0 (+https://www.embrapa.br)"
}

# URLs base
_BASE_URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"

# Mapeamentos de “subopções” usadas em Importação e Exportação
_IMPORT_CATEGORIES = {
    "Vinhos de mesa": "subopt_01",
    "Espumantes": "subopt_02",
    "Uvas frescas": "subopt_03",
    "Uvas passas": "subopt_04",
    "Suco de uva": "subopt_05",
}

_EXPORT_CATEGORIES = {
    "Vinhos de mesa": "subopt_01",
    "Espumantes": "subopt_02",
    "Uvas frescas": "subopt_03",
    "Suco de uva": "subopt_04",
}

# Subopções para Processamento
_PROCESS_CATEGORIES = {
    "Viníferas": "subopt_01",
    "Americanas e híbridas": "subopt_02",
    "Uvas de mesa": "subopt_03",
    "Sem classificação": "subopt_04",
}


# -------------------------------------------------------------------
# =====================< HELPERS INTERNOS >===========================
# -------------------------------------------------------------------

def _safe_get(url: str, params: dict = None) -> BeautifulSoup | None:
    """
    Faz uma requisição GET para a URL informada (com timeout e cabeçalhos).
    Se a resposta for HTTP 200, retorna um objeto BeautifulSoup com o conteúdo.
    Caso contrário (timeout, erro HTTP, etc.), retorna None.
    """
    try:
        resp = requests.get(url, params=params,
                            headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.RequestException as err:
        # Em produção, substitua por logger.error(f"... {err}")
        print(f"[HTTP ERROR] GET {url} with params={params}: {err}")
        return None


def _safe_post(url: str, data: dict) -> BeautifulSoup | None:
    """
    Faz uma requisição POST para a URL informada (com timeout e cabeçalhos).
    Se a resposta for HTTP 200, retorna um objeto BeautifulSoup com o conteúdo.
    Caso contrário, retorna None.
    """
    try:
        resp = requests.post(
            url, data=data, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.RequestException as err:
        # Em produção, substitua por logger.error(f"... {err}")
        print(f"[HTTP ERROR] POST {url} with data={data}: {err}")
        return None


def _clean_number_string(s: str) -> int:
    """
    Converte uma string numérica formatada (por ex. '1.234.567') em int.
    Se não for dígito, retorna 0.
    Subtrai o traço '-' para 0.
    """
    texto = s.replace(".", "").strip()
    return int(texto) if texto.isdigit() else 0


# services/scraper.py


# ----------------------------------------------------------------
# 1) Função auxiliar para “Processamento”
# ----------------------------------------------------------------

def _extract_table_categorizada(soup, etapa, categoria_uva, ano):
    """
    - etapa: string, ex: "Processamento"
    - categoria_uva: ex.: "Viníferas", "Americanas e híbridas", etc.
    - ano: inteiro (1970..2024)
    Retorna lista de dicionários:
      {
        "etapa": "Processamento",
        "categoria_uva": "<Viníferas | Americanas e híbridas | Uvas de mesa | Sem classificação>",
        "tipo_uva": "<TINTAS ou BRANCAS E ROSADAS>",
        "nome_uva": "<nome do cultivar>",
        "quantidade_kg": <int ou None>,
        "ano": <ano>
      }
    """
    tabela = soup.find("table", class_="tb_base tb_dados")
    resultados = []
    if not tabela:
        return resultados

    linhas = tabela.find_all("tr")
    tipo_uva_atual = None

    for linha in linhas:
        colunas = linha.find_all("td")
        # só processa linhas com exatamente 2 <td>
        if len(colunas) != 2:
            continue

        # pode ser “TINTAS”, “Ancelota”, etc.
        texto0 = colunas[0].get_text(strip=True)
        texto1 = colunas[1].get_text(strip=True)  # ex.: "139.320.884" ou "-"

        # Se <td class="tb_item"> → define um novo tipo de uva (“TINTAS” ou “BRANCAS E ROSADAS”)
        if "tb_item" in colunas[0].get("class", []):
            tipo_uva_atual = texto0

        # Se <td class="tb_subitem"> → é um cultivar dentro de tipo_uva_atual
        elif "tb_subitem" in colunas[0].get("class", []):
            # limpar pontos, definir int ou None:
            qt = texto1.replace(".", "").strip()
            if qt.isdigit():
                quantidade_kg = int(qt)
            else:
                quantidade_kg = None

            resultados.append({
                "etapa": etapa,                   # “Processamento”
                "categoria_uva": categoria_uva,   # ex.: “Viníferas”
                "tipo_uva": tipo_uva_atual,       # ex.: “TINTAS” ou “BRANCAS E ROSADAS”
                "nome_uva": texto0,               # ex.: “Ancelota”
                "quantidade_kg": quantidade_kg,   # ex.: 139320884 ou None
                "ano": ano                        # ex.: 1970
            })

    return resultados


# ----------------------------------------------------------------
# 2) get_processamento_data: varre de 1970 a 2024
# ----------------------------------------------------------------
def get_processamento_data():
    base_url = "http://vitibrasil.cnpuv.embrapa.br/index.php"
    subopcoes = {
        "Viníferas": "subopt_01",
        "Americanas e híbridas": "subopt_02",
        "Uvas de mesa": "subopt_03",
        "Sem classificação": "subopt_04"
    }
    todos = []

    for ano in range(1970, 2025):
        for categoria_uva, subopt in subopcoes.items():
            params = {"opcao": "opt_03", "subopcao": subopt, "ano": str(ano)}
            try:
                r = requests.get(base_url, params=params, timeout=10)
                r.encoding = "utf-8"
                soup = BeautifulSoup(r.text, "html.parser")
                todos.extend(
                    _extract_table_categorizada(
                        soup, "Processamento", categoria_uva, ano
                    )
                )
            except Exception as erro:
                print(
                    f"[Processamento] Erro em ({categoria_uva} - {ano}): {erro}")
                continue

    return todos


# -------------------------------------------------------------------
# ======================< PRODUÇÃO >===================================
# -------------------------------------------------------------------

def get_producao_data() -> list[dict]:
    """
    Faz scraping para todos os anos de 1970 a 2024 na aba Produção e
    retorna lista de dicionários:
      [
        {
          "etapa": "Produção",
          "categoria_produto": "<VINHO DE MESA|VINHO FINO|SUCO|DERIVADOS>",
          "tipo_produto": "<string ou '' para TOTAL>",
          "quantidade_l": "<string ou '' para TOTAL>",
          "ano": 1970
        },
        ...
      ]
    """
    all_data: list[dict] = []

    for ano in range(1970, 2025):
        url = f"{_BASE_URL}?opcao=opt_02&ano={ano}"
        soup = _safe_get(url)
        if soup is None:
            continue

        current_categoria = None
        rows = soup.select("table.tb_dados tbody tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) != 2:
                continue

            nome = cols[0].get_text(strip=True)
            valor = cols[1].get_text(strip=True)

            # Se for categoria de produto (classe="tb_item")
            if "tb_item" in cols[0].get("class", []):
                current_categoria = nome
                # Insere um “TOTAL” genérico, usando campos vazios em tipo_produto/quantidade_l
                all_data.append({
                    "etapa": "Produção",
                    "categoria_produto": current_categoria,
                    "tipo_produto": "",
                    "quantidade_l": "",
                    "ano": ano
                })
            # Se for subtipo (classe="tb_subitem")
            elif "tb_subitem" in cols[0].get("class", []):
                all_data.append({
                    "etapa": "Produção",
                    "categoria_produto": current_categoria,
                    "tipo_produto": nome,      # ex.: “Tinto”, “Branco”...
                    "quantidade_l": valor,     # ex.: “169.762.429”
                    "ano": ano
                })

    return all_data


# -------------------------------------------------------------------
# =================< COMERCIALIZAÇÃO >================================
# -------------------------------------------------------------------

def get_comercializacao_data() -> list[dict]:
    """
    Faz scraping para todos os anos de 1970 a 2024 na aba Comercialização e
    retorna lista de dicionários:
      [
        {
          "etapa": "Comercialização",
          "categoria_produto": "<VINHO DE MESA|VINHO FINO|VINHO FRIZANTE|…>",
          "produto": "<string ou '' para TOTAL>",
          "quantidade_l": "<string ou '' para TOTAL>",
          "ano": 1970
        },
        ...
      ]
    """
    all_data: list[dict] = []

    for ano in range(1970, 2025):
        url = f"{_BASE_URL}?opcao=opt_04&ano={ano}"
        soup = _safe_get(url)
        if soup is None:
            continue

        current_categoria = None
        rows = soup.select("table.tb_dados tbody tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) != 2:
                continue

            nome = cols[0].get_text(strip=True)
            valor = cols[1].get_text(strip=True)

            # Se for categoria de produto
            if "tb_item" in cols[0].get("class", []):
                current_categoria = nome
                all_data.append({
                    "etapa": "Comercialização",
                    "categoria_produto": current_categoria,
                    "produto": "",
                    "quantidade_l": "",
                    "ano": ano
                })
            # Se for subtipo de produto
            elif "tb_subitem" in cols[0].get("class", []):
                all_data.append({
                    "etapa": "Comercialização",
                    "categoria_produto": current_categoria,
                    "produto": nome,        # ex.: “Tinto”, “Rosado”...
                    "quantidade_l": valor,  # ex.: “187.016.848”
                    "ano": ano
                })

    return all_data


# -------------------------------------------------------------------
# =================< IMPORTAÇÃO >======================================
# -------------------------------------------------------------------


def get_importacao_data():
    BASE_URL = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05"
    CATEGORIAS = {
        "Vinhos de mesa": "subopt_01",
        "Espumantes":     "subopt_02",
        "Uvas frescas":   "subopt_03",
        "Uvas passas":    "subopt_04",
        "Suco de uva":    "subopt_05"
    }
    session = requests.Session()
    all_data = []

    for categoria_nome, subopcao in CATEGORIAS.items():
        for ano in range(1970, 2025):
            try:
                # Vamos imprimir o URL e os dados POST para debugging
                print(
                    f"[Importação] solicitando {BASE_URL} com subopcao={subopcao}, ano={ano}")
                response = session.post(
                    BASE_URL,
                    data={"subopcao": subopcao, "ano": str(ano)},
                    timeout=10
                )
                print(f"  → status_code: {response.status_code}")
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table", class_="tb_dados")
                if not table:
                    # Indica que não encontrou a tabela para este par (categoria, ano)
                    # print(f"    > Não encontrou <table class='tb_dados'> para {categoria_nome} - {ano}")
                    continue

                rows = table.find_all("tr")[1:]
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) != 3:
                        continue
                    pais = cols[0].text.strip()
                    quantidade = cols[1].text.strip().replace(
                        ".", "").replace("-", "0")
                    valor = cols[2].text.strip().replace(
                        ".", "").replace("-", "0")

                    all_data.append({
                        "etapa": "Importação",
                        "categoria_produto": categoria_nome,
                        "ano": ano,
                        "pais": pais,
                        "quantidade_kg": int(quantidade) if quantidade.isdigit() else 0,
                        "valor_usd": int(valor) if valor.isdigit() else 0
                    })

            except Exception as e:
                print(f"[Importação] Erro em ({categoria_nome} - {ano}): {e}")
                continue

    print(f"[Importação] total de registros coletados: {len(all_data)}")
    return all_data


# -------------------------------------------------------------------
# =================< EXPORTAÇÃO >=====================================
# -------------------------------------------------------------------


def get_exportacao_data():
    BASE_URL = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_06"
    CATEGORIAS = {
        "Vinhos de mesa": "subopt_01",
        "Espumantes":     "subopt_02",
        "Uvas frescas":   "subopt_03",
        "Suco de uva":    "subopt_04"
    }

    session = requests.Session()
    all_data = []

    for categoria_nome, subopcao in CATEGORIAS.items():
        for ano in range(1970, 2025):
            try:
                print(
                    f"[Exportação] solicitando {BASE_URL} com subopcao={subopcao}, ano={ano}")
                response = session.post(
                    BASE_URL,
                    data={"subopcao": subopcao, "ano": str(ano)},
                    timeout=10
                )
                print(f"  → status_code: {response.status_code}")
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table", class_="tb_dados")
                if not table:
                    # print(f"    > Sem tabela para {categoria_nome} - {ano}")
                    continue

                rows = table.find_all("tr")[1:]
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) != 3:
                        continue
                    pais = cols[0].text.strip()
                    quantidade = cols[1].text.strip().replace(
                        ".", "").replace("-", "0")
                    valor = cols[2].text.strip().replace(
                        ".", "").replace("-", "0")

                    all_data.append({
                        "etapa": "Exportação",
                        "categoria_produto": categoria_nome,
                        "ano": ano,
                        "pais": pais,
                        "quantidade_kg": int(quantidade) if quantidade.isdigit() else 0,
                        "valor_usd": int(valor) if valor.isdigit() else 0
                    })

            except Exception as e:
                print(f"[Exportação] Erro em ({categoria_nome} - {ano}): {e}")
                continue

    print(f"[Exportação] total de registros coletados: {len(all_data)}")
    return all_data
