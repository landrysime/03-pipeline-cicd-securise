#!/usr/bin/env bash
# Scan de sécurité local (hors Jenkins) — utile pour tester la démo « avant/après ».
# Usage : ./scripts/trivy-scan.sh
set -euo pipefail

SEVERITY="CRITICAL,HIGH"
mkdir -p reports

echo "==> 1/2  SCA : vulnérabilités des dépendances (app/)"
trivy fs --scanners vuln --severity "$SEVERITY" app/ | tee reports/trivy-deps.txt

echo
echo "==> 2/2  Build + scan de l'image"
docker build -t demo-app:local app/
trivy image --severity "$SEVERITY" demo-app:local | tee reports/trivy-image.txt

echo
echo "==> Barrière de sécurité (échoue si CRITICAL présent)"
if trivy image --severity CRITICAL --exit-code 1 demo-app:local >/dev/null 2>&1; then
    echo "✅ Aucune vulnérabilité CRITICAL — déploiement autorisé."
else
    echo "❌ Vulnérabilités CRITICAL détectées — déploiement BLOQUÉ."
    exit 1
fi
