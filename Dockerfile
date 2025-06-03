FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Adicione build-essential e wheel para evitar erros em pacotes nativos
RUN apt-get update && apt-get install -y \
    build-essential \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
