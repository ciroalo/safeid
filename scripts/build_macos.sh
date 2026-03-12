#!/usr/bin/env bash
set -euo pipefail

rm -rf build dist

pyinstaller SafeID.spec