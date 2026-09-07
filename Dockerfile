FROM python:3.12-slim

# Install system utilities and support for interactive terminal
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Ensure workspace directory exists
RUN mkdir -p /app/workspace

EXPOSE 5000

ENV PYTHONUNBUFFERED=1
ENV TERM=xterm-256color

CMD ["python", "app.py"]
