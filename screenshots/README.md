# Captures de preuve — Projet 03

À déposer ici au fur et à mesure du lab (noms suggérés) :

| Fichier | Étape prouvée |
|---|---|
| `01-stack-demarree.png` | Jenkins + SonarQube démarrés (`docker compose ps`) |
| `02-sonarqube-config-jenkins.png` | Serveur SonarQube configuré dans Jenkins |
| `03-pipeline-rouge-bloque.png` | Commit vulnérable → pipeline **rouge**, gate en échec |
| `04-sonarqube-vulnerabilites.png` | Vulnérabilités de code détectées (SonarQube) |
| `05-trivy-cve-dependances.png` | CVE des dépendances / image (Trivy) |
| `06-pipeline-vert-deploy.png` | Correctif → pipeline **vert**, déploiement autorisé |
| `07-quality-gate-passed.png` | Quality Gate SonarQube **PASSED** |
| `08-appli-deployee.png` | `curl /health` → appli sécurisée en ligne |
