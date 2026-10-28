# ⚠️ IMAGE DE BASE VOLONTAIREMENT ANCIENNE (démo Trivy image scan).
# python:3.9-slim-buster repose sur Debian 10 (buster), qui porte de nombreuses
# CVE système connues. Le scan d'image Trivy doit les remonter et bloquer le déploiement.
# La version corrigée utilise une image récente (voir docs/GUIDE-LAB.md).
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
