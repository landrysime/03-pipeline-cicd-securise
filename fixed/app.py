"""
Application de démonstration — VERSION CORRIGÉE (Projet 03).

Les 5 vulnérabilités de la version initiale sont ici corrigées. Appliquer ce
fichier (le copier dans app/) constitue le 2ᵉ commit de la démo « avant/après » :
le pipeline doit alors passer au VERT.

Secrets : chargés depuis l'environnement, jamais en dur (voir .env, non committé).
"""
import os
import sqlite3
import subprocess

import yaml
from flask import Flask, request

app = Flask(__name__)

# CORRIGÉ 1 — secrets lus depuis l'environnement, pas en dur
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
API_TOKEN = os.environ.get("API_TOKEN", "")


@app.route("/user")
def get_user():
    # CORRIGÉ 2 — requête paramétrée (plus d'injection SQL)
    user_id = request.args.get("id", "")
    conn = sqlite3.connect("app.db")
    rows = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchall()
    return {"rows": rows}


@app.route("/ping")
def ping():
    # CORRIGÉ 3 — pas de shell, argument passé en liste + validation
    host = request.args.get("host", "127.0.0.1")
    if not all(c.isalnum() or c in ".-" for c in host):
        return {"error": "hôte invalide"}, 400
    output = subprocess.check_output(["ping", "-c", "1", host])
    return {"output": output.decode(errors="ignore")}


@app.route("/config", methods=["POST"])
def load_config():
    # CORRIGÉ 4 — désérialisation sûre
    config = yaml.safe_load(request.get_data())
    return {"config": str(config)}


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # CORRIGÉ 5 — debug désactivé
    app.run(host="0.0.0.0", port=5000, debug=False)
