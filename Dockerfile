FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /app/

EXPOSE 5000

# Ajuste importante: menos workers e mais tempo para requisições
CMD ["gunicorn", "--workers=1", "--timeout=180", "--bind=0.0.0.0:5000", "app:app"]
