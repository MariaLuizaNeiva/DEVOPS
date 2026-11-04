# syntax=docker/dockerfile:1

# ---------- Estágio 1: build das dependências ----------
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
# Instala as dependências em um prefixo isolado (copiado depois para a imagem final)
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Estágio 2: imagem final (enxuta) ----------
FROM python:3.11-slim

# Versão da aplicação (injetada no build pela pipeline de CD: --build-arg APP_VERSION=1.0.0)
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Usuário sem privilégios (boa prática de segurança: não rodar como root)
RUN useradd --system --uid 10001 --no-create-home app

WORKDIR /app
COPY --from=builder /install /usr/local
COPY app.py storage.py ./

USER app
EXPOSE 5000

# Healthcheck sem depender de curl (imagem slim não o possui)
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health', timeout=2)" || exit 1

# Servidor de produção (gunicorn) no lugar do servidor de desenvolvimento do Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
