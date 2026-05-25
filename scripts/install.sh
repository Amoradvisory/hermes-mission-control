#!/usr/bin/env bash
# Hermes Mission Control -- Script d'installation V0
# Non intrusif : ne touche pas a Hermes existant.

set -euo pipefail

echo "[HMC] Installation Hermes Mission Control V0"
echo "[HMC] Ce script installe uniquement les dependances Python du plugin."
echo "[HMC] Il ne modifie pas Hermes, config.yaml, ou tout autre fichier du coeur."
echo ""

# Verifier Python
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
  echo "[HMC] ERREUR : Python 3.10+ requis. Installez Python puis relancez."
  exit 1
fi

PY=$(command -v python3 || command -v python)
echo "[HMC] Python detecte : $($PY --version)"

# Installer les dependances
echo "[HMC] Installation des dependances : fastapi uvicorn pyyaml pytest"
$PY -m pip install fastapi uvicorn pyyaml pytest --quiet

echo ""
echo "[HMC] Installation terminee."
echo "[HMC] Lancer l'API : python dashboard/plugin_api.py"
echo "[HMC] Lancer les tests : python -m pytest tests/"
echo "[HMC] Sante API : http://127.0.0.1:7700/health"
