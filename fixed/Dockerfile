# VERSION CORRIGÉE — image de base récente (Debian 12 bookworm), surface d'attaque réduite.
FROM python:3.12-slim-bookworm

WORKDIR /app

# Mises à jour système
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# CORRIGÉ — exécution en utilisateur non-root
RUN useradd -m appuser
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
