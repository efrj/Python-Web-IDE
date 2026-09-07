FROM python:3.12-slim

# Instalar utilitários de sistema e suporte ao terminal interativo
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar arquivos da aplicação
COPY . /app

# Garantir que a pasta workspace exista
RUN mkdir -p /app/workspace

EXPOSE 5000

ENV PYTHONUNBUFFERED=1
ENV TERM=xterm-256color

CMD ["python", "app.py"]
