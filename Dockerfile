FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /app/

# Expor porta em que o App irá escutar
EXPOSE 5000

# Comando de inicialização: 
# usamos 4 workers (ajuste conforme CPU) e bind 0.0.0.0:5000
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
