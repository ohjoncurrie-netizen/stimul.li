#!/usr/bin/env bash
set -euo pipefail

PID_FILE="${1:-/run/stimuli-api/gunicorn.pid}"

if [[ ! -f "${PID_FILE}" ]]; then
  echo "Gunicorn PID file not found: ${PID_FILE}" >&2
  exit 1
fi

MASTER_PID="$(cat "${PID_FILE}")"
if [[ -z "${MASTER_PID}" ]] || ! kill -0 "${MASTER_PID}" 2>/dev/null; then
  echo "Gunicorn master process is not running." >&2
  exit 1
fi

echo "Sending HUP to Gunicorn master process ${MASTER_PID} for a graceful reload..."
kill -HUP "${MASTER_PID}"
echo "Reload signal sent."
