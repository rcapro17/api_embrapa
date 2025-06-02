import logging
from services import scraper
import pytest


class LogCapture:
    def __init__(self):
        self.records = []

    def __call__(self, record):
        self.records.append(record)


@pytest.fixture
def capture_logs(monkeypatch):
    log_capture = LogCapture()
    monkeypatch.setattr(logging.getLogger(
        'api_embrapa').handlers[0], 'emit', log_capture)
    return log_capture


def test_logging_scraper_get_producao_data(capture_logs):
    scraper.get_producao_data()
    messages = [r.getMessage() for r in capture_logs.records]
    assert any("Iniciando scraping de Produção" in msg for msg in messages)
    assert any("Scraping de Produção completo" in msg for msg in messages)
