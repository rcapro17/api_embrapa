# test/test_scraper.py

import pytest
from services.scraper import (
    get_producao_data,
    get_processamento_data,
    get_comercializacao_data,
    get_importacao_data,
    get_exportacao_data
)


def test_get_producao_data():
    data = get_producao_data(ano_inicio=2022, ano_fim=2023)
    assert isinstance(data, list)
    exemplo = data[0]
    chaves_obrigatorias = {"etapa", "categoria_produto",
                           "tipo_produto", "quantidade_l", "ano"}
    assert all(ch in exemplo for ch in chaves_obrigatorias)
    assert all(item["etapa"] == "Produção" for item in data)


def test_get_processamento_data():
    data = get_processamento_data(ano_inicio=2022, ano_fim=2023)
    assert isinstance(data, list)
    exemplo = data[0]
    chaves_obrigatorias = {"etapa", "categoria_uva",
                           "tipo_uva", "nome_uva", "quantidade_kg", "ano"}
    assert all(ch in exemplo for ch in chaves_obrigatorias)
    assert all(item["etapa"] == "Processamento" for item in data)


def test_get_comercializacao_data():
    data = get_comercializacao_data(ano_inicio=2022, ano_fim=2023)
    assert isinstance(data, list)
    exemplo = data[0]
    chaves_obrigatorias = {"etapa", "categoria_produto",
                           "produto", "quantidade_l", "ano"}
    assert all(ch in exemplo for ch in chaves_obrigatorias)
    assert all(item["etapa"] == "Comercialização" for item in data)


def test_get_importacao_data():
    data = get_importacao_data(ano_inicio=2022, ano_fim=2023)
    assert isinstance(data, list)
    exemplo = data[0]
    chaves_obrigatorias = {"etapa", "categoria_produto",
                           "ano", "pais", "quantidade_kg", "valor_usd"}
    assert all(ch in exemplo for ch in chaves_obrigatorias)
    assert all(item["etapa"] == "Importação" for item in data)


def test_get_exportacao_data():
    data = get_exportacao_data(ano_inicio=2022, ano_fim=2023)
    assert isinstance(data, list)
    exemplo = data[0]
    chaves_obrigatorias = {"etapa", "categoria_produto",
                           "ano", "pais", "quantidade_kg", "valor_usd"}
    assert all(ch in exemplo for ch in chaves_obrigatorias)
    assert all(item["etapa"] == "Exportação" for item in data)
