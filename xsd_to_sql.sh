#!/bin/bash

DIRNAME="$(dirname "$0")"

MAIN_PROG="${DIRNAME}/main.py"
PYTHON_BIN="${PYTHON_BIN:-python3}"

"${PYTHON_BIN}" "${MAIN_PROG}" "$@"
