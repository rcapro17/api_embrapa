# Dockerfile

# 1. Use uma imagem leve de Python
FROM python:3.11-slim

# 2. Defina o diretório de trabalho dentro do container
WORKDIR /app

# 3. Copie o requirements.txt (ou Pipfile) e instale as dependências
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copie todo o conteúdo do projeto para /app
COPY . .

# 5. Expõe a porta em que o Flask irá rodar
EXPOSE 5000

# 6. Command padrão (mas será sobrescrito pelo docker‐compose “command”)
CMD ["python", "app.py"]
