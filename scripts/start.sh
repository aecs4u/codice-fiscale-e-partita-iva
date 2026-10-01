#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

START_APP_NAME="Codice Fiscale"
START_APP_MODULE="codice_fiscale.main:app"
START_DEFAULT_PORT=8003
START_DEFAULT_HOST="0.0.0.0"
START_PROJECT_ROOT="${PROJECT_ROOT}"
START_SKIP_SYNC="${START_SKIP_SYNC:-true}"

SHARED_START="${PROJECT_ROOT}/../bin/start-common.sh"
source "${SHARED_START}"
start_common_main "$@"

