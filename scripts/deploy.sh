#!/usr/bin/env bash
# Faz o deploy de uma versão da imagem usando Docker Compose.
# Uso: scripts/deploy.sh <versão>      ex.: scripts/deploy.sh 1.0.0
# Variáveis esperadas: APP_IMAGE (ex.: ghcr.io/usuario/repo) e POSTGRES_PASSWORD.
set -euo pipefail

VERSION="${1:?Uso: deploy.sh <versão>}"
VERSION="${VERSION#v}"                       # aceita "v1.0.0" ou "1.0.0"
: "${APP_IMAGE:?Defina APP_IMAGE (ex.: ghcr.io/usuario/repo)}"

export APP_VERSION="$VERSION"
echo ">> Deploy da versão ${APP_VERSION} (${APP_IMAGE}:${APP_VERSION})"

docker compose pull app
docker compose up -d --no-build --wait --wait-timeout 90
docker compose ps
