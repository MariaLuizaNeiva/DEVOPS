#!/usr/bin/env bash
# Valida que a versão esperada está de pé e saudável.
# Uso: scripts/smoke_test.sh <versão esperada>
# HEALTH_PATH permite simular uma falha (ex.: HEALTH_PATH=/rota-inexistente).
set -euo pipefail

EXPECTED="${1:?Uso: smoke_test.sh <versão esperada>}"
EXPECTED="${EXPECTED#v}"
BASE_URL="${BASE_URL:-http://localhost:5000}"
HEALTH_PATH="${HEALTH_PATH:-/health}"

echo ">> Smoke test: GET ${BASE_URL}${HEALTH_PATH}"
curl --fail --silent --show-error --retry 15 --retry-delay 3 --retry-connrefused --retry-all-errors \
     "${BASE_URL}${HEALTH_PATH}"
echo

echo ">> Smoke test: GET ${BASE_URL}/version"
RESPONSE="$(curl --fail --silent --show-error "${BASE_URL}/version")"
echo "${RESPONSE}"

ACTUAL="$(printf '%s' "${RESPONSE}" | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])")"
if [ "${ACTUAL}" != "${EXPECTED}" ]; then
  echo "ERRO: versão em execução (${ACTUAL}) difere da esperada (${EXPECTED})" >&2
  exit 1
fi
echo "OK: versão ${ACTUAL} saudável"
