#!/usr/bin/env bash
# Vera container entrypoint.
# First boot: seed the Vera layer into the /opt/data volume (setup.sh,
# non-interactive, answers from env vars). Every boot: run Hermes.
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-/opt/data}"
export HERMES_HOME
mkdir -p "$HERMES_HOME"

if [ ! -f "$HERMES_HOME/.vera-seeded" ]; then
  echo "[vera] first boot - seeding Vera layer into $HERMES_HOME"
  if VERA_SKIP_HELLO=1 /opt/vera/setup/setup.sh --non-interactive; then
    touch "$HERMES_HOME/.vera-seeded"
    echo "[vera] seeded. Vera introduces herself on first message - say hello."
  else
    echo "[vera] seed failed - check env vars against .env.example" >&2
    exit 1
  fi
fi

exec hermes "$@"
