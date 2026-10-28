# Guide du lab — Pipeline CI/CD sécurisé (reproductible)

Un tiers doit pouvoir rejouer le lab de A à Z. Environnement : **Docker + Docker Compose** sur un poste (Linux, WSL2 ou Docker Desktop).

> 💡 **Ressources** : SonarQube + Jenkins demandent ~4 Go de RAM. Si ton poste est juste, voir la section « Variante légère » en bas.

## 1. Prérequis

```bash
docker --version
docker compose version
```
Si absent : installer Docker Desktop (Windows/Mac) ou Docker Engine + plugin compose (Linux).

## 2. Démarrer la stack CI

```bash
git clone https://github.com/landrysime/03-pipeline-cicd-securise.git
cd 03-pipeline-cicd-securise
docker compose up -d --build        # construit l'image Jenkins (Docker CLI + Trivy) puis lance tout
docker compose ps                   # jenkins, sonarqube, sonar-db doivent être "running"
```

- Jenkins : http://localhost:8080
- SonarQube : http://localhost:9000  (login initial `admin` / `admin`)

**Déverrouiller Jenkins** (1ʳᵉ fois) :
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
→ coller le mot de passe, installer les plugins suggérés, créer l'utilisateur admin.
📸 *Capture : Jenkins et SonarQube démarrés.*

## 3. Connecter Jenkins à SonarQube

1. **SonarQube** → My Account → Security → générer un **token** (`jenkins-token`).
2. **Jenkins** → Administration → Credentials → ajouter un *Secret text* avec ce token (id : `sonar-token`).
3. **Jenkins** → Administration → System → section *SonarQube servers* :
   - Name : `sonarqube`
   - Server URL : `http://sonarqube:9000`
   - Token : `sonar-token`
4. **Jenkins** → Administration → Tools → *SonarQube Scanner* : installer automatiquement la dernière version.

📸 *Capture : configuration du serveur SonarQube dans Jenkins.*

## 4. Créer le job pipeline

Jenkins → New Item → **Pipeline** → nom `demo-app-securise` :
- *Pipeline script from SCM* → Git → URL du dépôt → branche `main` → script `Jenkinsfile`.
- Save.

## 5. Démo « AVANT » — le commit vulnérable est BLOQUÉ 🔴

Le dépôt est livré avec la version **vulnérable** (`app/`). Lance le pipeline :

Jenkins → `demo-app-securise` → **Build Now**.

Résultat attendu : le pipeline **échoue** à une barrière de sécurité :
- **SonarQube** remonte les vulnérabilités du code (injection SQL, commande, secret en dur, `yaml.load`, debug) → Quality Gate **FAILED**, ou
- **Trivy** remonte les CVE des dépendances / de l'image → `--exit-code 1` → stage **rouge**.

📸 *Captures (preuves clés) :*
- *Jenkins : pipeline rouge, stage de sécurité en échec.*
- *SonarQube : tableau des vulnérabilités détectées.*
- *Trivy : liste des CVE CRITICAL/HIGH.*

## 6. Démo « APRÈS » — le correctif PASSE 🟢

Applique la version corrigée (fournie dans `fixed/`) :

```bash
cp fixed/app.py app/app.py
cp fixed/requirements.txt app/requirements.txt
cp fixed/Dockerfile app/Dockerfile
git add app/ && git commit -m "fix: correction des vulnerabilites (deps, code, image)"
git push
```

Relance **Build Now**. Cette fois :
- SonarQube : Quality Gate **PASSED**,
- Trivy : plus de CVE bloquante,
- 🚦 **Security Gate franchi** → stage **Deploy** exécuté → conteneur `demo-app-prod` lancé.

```bash
curl http://localhost:5000/health      # {"status":"ok"} : l'appli sécurisée tourne
```

📸 *Captures : pipeline entièrement vert + Quality Gate PASSED + appli déployée.*

## 7. Ce que chaque barrière prouve

| Barrière | Outil | Ce qu'elle bloque |
|---|---|---|
| SAST + Quality Gate | SonarQube | Vulnérabilités **du code** (injection, secrets, désérialisation) |
| SCA | Trivy fs | CVE des **dépendances** (Flask, PyYAML, requests…) |
| Scan image | Trivy image | CVE **système** de l'image de base |
| Security Gate | Trivy (`--exit-code 1`) | Tout déploiement d'une image avec CVE CRITICAL |

## Variante légère (peu de RAM)

Si SonarQube ne tient pas sur le poste, la chaîne **Trivy seule** suffit à démontrer le gate (SCA + image + blocage) :
```bash
./scripts/trivy-scan.sh        # version vulnérable → BLOQUÉ
cp fixed/* app/                # applique le correctif
./scripts/trivy-scan.sh        # → AUTORISÉ
```
On garde alors SonarQube en bonus documenté (captures d'une exécution ponctuelle).
