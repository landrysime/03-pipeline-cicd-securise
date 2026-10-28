# Projet 03 — Pipeline CI/CD sécurisé (DevSecOps)

Chaîne d'intégration continue qui **intègre la sécurité au pipeline** (« shift-left ») et **bloque automatiquement le déploiement** de code ou d'images vulnérables, avec démonstration **avant / après** (pipeline rouge → vert).

**Stack :** Jenkins · SonarQube · Trivy · Docker · Docker Compose · Python/Flask

---

## 🎯 Contexte — *NovaPay*, une PME éditrice de logiciel

**NovaPay** édite une application SaaS de paiements, livrée **plusieurs fois par jour**. La sécurité y est un contrôle manuel trimestriel — insuffisant à ce rythme. En 6 mois : une **dépendance vulnérable** (type Log4Shell) restée en production, un **secret en dur** poussé sur Git, et un **audit client raté** faute de pouvoir prouver que code et conteneurs sont scannés à chaque livraison (contrat suspendu).

**Mission (DevSecOps) :** faire en sorte qu'un code ou une image vulnérable ne puisse **plus jamais atteindre la production — automatiquement, sans ralentir les développeurs**. C'est le principe du *shift-left* : la sécurité **dans** le pipeline, pas à côté.

> Scénario détaillé, mapping problème → solution et valeur métier : **[`docs/CONTEXTE-ENTREPRISE.md`](docs/CONTEXTE-ENTREPRISE.md)**.

## 🔧 Le pipeline

```
Commit ─▶ Tests ─▶ SAST (SonarQube) ─▶ Quality Gate ─▶ SCA (Trivy deps)
      ─▶ Build image ─▶ Scan image (Trivy) ─▶ 🚦 Security Gate ─▶ Deploy
```

Chaque barrière peut **arrêter** le pipeline :

| Barrière | Outil | Ce qu'elle détecte |
|---|---|---|
| SAST + Quality Gate | SonarQube | Vulnérabilités du **code** : injection SQL, injection de commande, secret en dur, désérialisation non sûre, debug activé |
| SCA | Trivy (`fs`) | CVE des **dépendances** (Flask, PyYAML, requests, Jinja2, Werkzeug) |
| Scan image | Trivy (`image`) | CVE **système** de l'image de base |
| Security Gate | Trivy `--exit-code 1` | Refuse tout déploiement d'une image contenant une CVE **CRITICAL** |

## 🗂️ Structure du dépôt

```
app/                     # appli démo (version VULNÉRABLE)
  app.py                 # 5 vulnérabilités de code volontaires
  requirements.txt       # 5 dépendances avec CVE connues
  Dockerfile             # image de base ancienne (CVE système)
  tests/
fixed/                   # version CORRIGÉE (pour la démo avant/après)
ci/jenkins/              # image Jenkins outillée (Docker CLI + Trivy)
Jenkinsfile              # définition du pipeline
docker-compose.yml       # Jenkins + SonarQube + PostgreSQL
sonar-project.properties # config analyse SonarQube
scripts/trivy-scan.sh    # scan local (variante sans Jenkins)
docs/GUIDE-LAB.md        # procédure complète A→Z
screenshots/             # preuves
```

## 🔴🟢 Démonstration avant / après (le cœur du projet)

| Étape | Version déployée | Résultat du pipeline |
|---|---|---|
| **Avant** | `app/` (vulnérable) | 🔴 **Bloqué** — Quality Gate FAILED / Trivy `exit 1` : pas de déploiement |
| **Après** | `fixed/` appliqué | 🟢 **Vert** — toutes les barrières passées → déploiement autorisé |

Cette bascule prouve que la chaîne **empêche réellement** une régression de sécurité d'atteindre la production.

## ▶️ Reproduire

Procédure complète : **[`docs/GUIDE-LAB.md`](docs/GUIDE-LAB.md)**. En résumé :
```bash
docker compose up -d --build        # Jenkins :8080 · SonarQube :9000
# configurer le token SonarQube dans Jenkins, créer le job pipeline (from SCM)
# Build Now sur la version vulnérable  -> pipeline ROUGE
cp fixed/* app/ && git commit -am "fix"  # applique le correctif
# Build Now                               -> pipeline VERT + déploiement
```

Variante légère (peu de RAM) : `./scripts/trivy-scan.sh` démontre le gate avec Trivy seul.

## 🎓 Compétences démontrées

DevSecOps · intégration de la sécurité dans un pipeline CI/CD (Jenkins) · analyse statique SAST (SonarQube + Quality Gate) · analyse de composition SCA et scan d'image de conteneur (Trivy) · security gate bloquant · remédiation de vulnérabilités (code, dépendances, image) · conteneurisation (Docker) · documentation reproductible.

---

*Projet réalisé en autonomie — Styve Landry SIME KOUNOU — styvelandry1@outlook.fr — octobre 2026*
