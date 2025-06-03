# services/scraper.py

import requests
from bs4 import BeautifulSoup
from logging_config import logger

# =============< CONFIGURAÇÕES GERAIS >===============================

REQUEST_TIMEOUT = 10

HTTP_HEADERS = {
    "User-Agent": "Embrapa-Data-Scraper/1.0 (+https://www.embrapa.br)"
}

_BASE_URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"

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

_PROCESS_CATEGORIES = {
    "Viníferas": "subopt_01",
    "Americanas e híbridas": "subopt_02",
    "Uvas de mesa": "subopt_03",
    "Sem classificação": "subopt_04",
}


# =====================< HELPERS INTERNOS >===========================

def _safe_get(url: str, params: dict = None) -> BeautifulSoup | None:
    logger.info(f"[GET] {url} | params={params}")
    try:
        resp = requests.get(url, params=params,
                            headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.RequestException as err:
        logger.error(f"[HTTP ERROR] GET {url} with params={params}: {err}")
        return None


def _safe_post(url: str, data: dict) -> BeautifulSoup | None:
    logger.info(f"[POST] {url} | data={data}")
    try:
        resp = requests.post(
            url, data=data, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.RequestException as err:
        logger.error(f"[HTTP ERROR] POST {url} with data={data}: {err}")
        return None


def _clean_number_string(s: str) -> int:
    texto = s.replace(".", "").strip()
    return int(texto) if texto.isdigit() else 0


def _extract_table_categorizada(soup, etapa, categoria_uva, ano):
    tabela = soup.find("table", class_="tb_base tb_dados")
    resultados = []
    if not tabela:
        logger.warning(
            f"[{etapa}] Nenhuma tabela encontrada para {categoria_uva} - {ano}")
        return resultados

    linhas = tabela.find_all("tr")
    tipo_uva_atual = None

    for linha in linhas:
        colunas = linha.find_all("td")
        if len(colunas) != 2:
            continue

        texto0 = colunas[0].get_text(strip=True)
        texto1 = colunas[1].get_text(strip=True)

        if "tb_item" in colunas[0].get("class", []):
            tipo_uva_atual = texto0

        elif "tb_subitem" in colunas[0].get("class", []):
            qt = texto1.replace(".", "").strip()
            if qt.isdigit():
                quantidade_kg = int(qt)
            else:
                quantidade_kg = None

            resultados.append({
                "etapa": etapa,
                "categoria_uva": categoria_uva,
                "tipo_uva": tipo_uva_atual,
                "nome_uva": texto0,
                "quantidade_kg": quantidade_kg,
                "ano": ano
            })

    return resultados


def get_processamento_data(ano_inicio=2020, ano_fim=2024):
    logger.info(
        f"Iniciando scraping de Processamento ({ano_inicio}-{ano_fim})")
    base_url = _BASE_URL
    subopcoes = _PROCESS_CATEGORIES
    todos = []
    session = requests.Session()

    for ano in range(ano_inicio, ano_fim + 1):
        for categoria_uva, subopt in subopcoes.items():
            params = {"opcao": "opt_03", "subopcao": subopt, "ano": str(ano)}
            try:
                r = session.get(base_url, params=params, timeout=10)
                r.encoding = "utf-8"
                soup = BeautifulSoup(r.text, "html.parser")
                todos.extend(
                    _extract_table_categorizada(
                        soup, "Processamento", categoria_uva, ano
                    )
                )
            except Exception as erro:
                logger.error(
                    f"[Processamento] Erro em ({categoria_uva} - {ano}): {erro}")
                continue

    logger.info(f"Scraping de Processamento completo: {len(todos)} registros")
    return todos


def get_producao_data(ano_inicio: int = 1970, ano_fim: int = 2024) -> list[dict]:
    """
    Faz scraping dos dados da aba Produção entre ano_inicio e ano_fim.
    Retorna uma lista de dicionários:
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

    for ano in range(ano_inicio, ano_fim + 1):
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

            if "tb_item" in cols[0].get("class", []):
                current_categoria = nome
                all_data.append({
                    "etapa": "Produção",
                    "categoria_produto": current_categoria,
                    "tipo_produto": "",
                    "quantidade_l": "",
                    "ano": ano
                })
            elif "tb_subitem" in cols[0].get("class", []):
                all_data.append({
                    "etapa": "Produção",
                    "categoria_produto": current_categoria,
                    "tipo_produto": nome,
                    "quantidade_l": valor,
                    "ano": ano
                })

    return all_data


def get_comercializacao_data(ano_inicio: int = 1970, ano_fim: int = 2024) -> list[dict]:
    """
    Faz scraping dos dados da aba Comercialização entre ano_inicio e ano_fim.
    Retorna uma lista de dicionários:
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

    for ano in range(ano_inicio, ano_fim + 1):
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

            if "tb_item" in cols[0].get("class", []):
                current_categoria = nome
                all_data.append({
                    "etapa": "Comercialização",
                    "categoria_produto": current_categoria,
                    "produto": "",
                    "quantidade_l": "",
                    "ano": ano
                })
            elif "tb_subitem" in cols[0].get("class", []):
                all_data.append({
                    "etapa": "Comercialização",
                    "categoria_produto": current_categoria,
                    "produto": nome,
                    "quantidade_l": valor,
                    "ano": ano
                })

    return all_data


def get_importacao_data(ano_inicio=2020, ano_fim=2024):
    logger.info(f"Iniciando scraping de Importação ({ano_inicio}-{ano_fim})")
    BASE_URL = f"{_BASE_URL}?opcao=opt_05"
    CATEGORIAS = _IMPORT_CATEGORIES
    session = requests.Session()
    all_data = []

    for categoria_nome, subopcao in CATEGORIAS.items():
        for ano in range(ano_inicio, ano_fim + 1):
            try:
                logger.info(
                    f"[Importação] solicitando ano={ano}, categoria={categoria_nome}")
                response = session.post(
                    BASE_URL,
                    data={"subopcao": subopcao, "ano": str(ano)},
                    timeout=10
                )
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table", class_="tb_dados")
                if not table:
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
                logger.error(
                    f"[Importação] Erro em ({categoria_nome} - {ano}): {e}")
                continue

    logger.info(f"Scraping de Importação completo: {len(all_data)} registros")
    return all_data


def get_exportacao_data(ano_inicio=2020, ano_fim=2024):
    logger.info(f"Iniciando scraping de Exportação ({ano_inicio}-{ano_fim})")
    BASE_URL = f"{_BASE_URL}?opcao=opt_06"
    CATEGORIAS = _EXPORT_CATEGORIES
    session = requests.Session()
    all_data = []

    for categoria_nome, subopcao in CATEGORIAS.items():
        for ano in range(ano_inicio, ano_fim + 1):
            try:
                logger.info(
                    f"[Exportação] solicitando ano={ano}, categoria={categoria_nome}")
                response = session.post(
                    BASE_URL,
                    data={"subopcao": subopcao, "ano": str(ano)},
                    timeout=10
                )
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table", class_="tb_dados")
                if not table:
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
                logger.error(
                    f"[Exportação] Erro em ({categoria_nome} - {ano}): {e}")
                continue

    logger.info(f"Scraping de Exportação completo: {len(all_data)} registros")
    return all_data
