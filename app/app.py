"""
Application de démonstration — Projet 03 (pipeline CI/CD sécurisé).

⚠️  CE FICHIER CONTIENT DES VULNÉRABILITÉS VOLONTAIRES.
    Elles servent à prouver que la chaîne CI/CD (SonarQube + Trivy) les détecte
    et BLOQUE le déploiement. La version corrigée est fournie dans le projet
    (voir docs/GUIDE-LAB.md, démo « avant / après »).

    NE PAS déployer cette version en production.
"""
import sqlite3
import subprocess

import yaml
from flask import Flask, request

app = Flask(__name__)

# VULN 1 — secret en dur dans le code (SonarQube : security hotspot / bug)
DB_PASSWORD = "SuperSecret123!"
API_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuv"


@app.route("/user")
def get_user():
    # VULN 2 — injection SQL : la saisie utilisateur est concaténée dans la requête
    user_id = request.args.get("id", "")
    conn = sqlite3.connect("app.db")
    query = "SELECT * FROM users WHERE id = '%s'" % user_id  # nosec? non : vulnérable
    rows = conn.execute(query).fetchall()
    return {"rows": rows}


@app.route("/ping")
def ping():
    # VULN 3 — injection de commande : shell=True avec une entrée non filtrée
    host = request.args.get("host", "127.0.0.1")
    output = subprocess.check_output("ping -c 1 " + host, shell=True)
    return {"output": output.decode(errors="ignore")}


@app.route("/config", methods=["POST"])
def load_config():
    # VULN 4 — désérialisation YAML non sûre (exécution de code arbitraire)
    data = request.get_data()
    config = yaml.load(data)  # devrait être yaml.safe_load
    return {"config": str(config)}


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # VULN 5 — debug activé + écoute sur toutes les interfaces
    app.run(host="0.0.0.0", port=5000, debug=True)
