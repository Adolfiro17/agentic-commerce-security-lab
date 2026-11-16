#!/usr/bin/env bash
# One command to run the Adolfiro Market AI commerce lab.
# No API key and no cloud account. The only network use is the first `pip install`.
#
#   ./start.sh              open the lab in your browser (http://localhost:8501)
#   ./start.sh matrix       run every attack in both modes and print the result table
#   ./start.sh run 3        run one module in the terminal (add: --mode vulnerable)
#   ./start.sh test         run the test suite
#   ./start.sh site         serve the course site at http://localhost:8000
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"
if [ ! -d .venv ]; then
  "$PY" -m venv .venv 2>/dev/null || {
    echo "Could not create a virtual environment."
    echo "On Debian/Ubuntu run: sudo apt update && sudo apt install -y python3-venv"
    exit 1
  }
fi
# shellcheck disable=SC1091
. .venv/bin/activate
pip install -q -r requirements.txt

cmd="${1:-app}"
[ "$#" -gt 0 ] && shift
case "$cmd" in
  app)    echo "Opening the lab at http://localhost:8501 (Ctrl+C to stop)"; python -m streamlit run app.py ;;
  matrix) python -m shop.cli matrix ;;
  run)    python -m shop.cli run "$@" ;;
  test)   python -m pytest -q ;;
  site)   echo "Serving http://localhost:8000 (Ctrl+C to stop)"; python -m http.server 8000 --directory docs ;;
  *)      python -m shop.cli "$cmd" "$@" ;;
esac
