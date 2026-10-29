# Parcours pas à pas — Projet 03 (du début au livrable)

Ce guide t'accompagne de zéro jusqu'au rendu final, en expliquant à chaque étape **ce qu'on fait** et **pourquoi**. Objectif : que tu comprennes la logique, pas seulement les commandes.

---

## Partie 0 — Comprendre l'objectif (le « pourquoi » global)

**Ce qu'on fait :** on construit une chaîne CI/CD qui teste la sécurité **automatiquement** à chaque livraison de code, et qui **bloque** le déploiement si une faille est trouvée.

**Pourquoi :** dans une vraie entreprise (scénario NovaPay), on livre plusieurs fois par jour. Contrôler la sécurité à la main, une fois par trimestre, laisse passer des failles en production (dépendance vulnérable, secret en dur). On déplace donc le contrôle **au plus tôt**, dans le pipeline — c'est le principe « **shift-left** ».

**Les 3 types de failles qu'on va attraper :**
| Type | Outil | Exemple |
|---|---|---|
| Faille dans **le code** | SonarQube (SAST) | injection SQL, secret en dur |
| Faille dans **les dépendances** | Trivy (SCA) | librairie avec une CVE connue |
| Faille dans **l'image conteneur** | Trivy (image) | image de base obsolète |

---

## Partie 1 — Préparer le terrain

**Ce qu'on fait :** on installe Docker et on récupère le projet.

**Pourquoi :** toute la chaîne (Jenkins, SonarQube, l'appli) tourne dans des **conteneurs**. Avantage : rien à installer « en dur » sur ton PC, et c'est **reproductible** à l'identique sur n'importe quelle machine (un critère noté).

```bash
docker --version
docker compose version
git clone https://github.com/landrysime/03-pipeline-cicd-securise.git
cd 03-pipeline-cicd-securise
```

---

## Partie 2 — Comprendre l'appli démo (le « patient »)

**Ce qu'on fait :** on regarde l'appli `app/` — une petite appli Flask **volontairement vulnérable**.

**Pourquoi volontairement vulnérable :** pour **prouver** que la chaîne détecte et bloque. Un pipeline qui laisse tout passer ne prouve rien. On a besoin d'un « patient malade » pour montrer que le « médecin » (le pipeline) fait son travail.

**Ce qu'elle contient :**
- `app.py` : 5 failles de code (injection SQL, injection de commande, secret en dur, `yaml.load` non sûr, debug activé) → cibles de **SonarQube**.
- `requirements.txt` : 5 dépendances avec CVE connues → cibles de **Trivy**.
- `Dockerfile` : image de base ancienne (Debian buster) → cible du **scan d'image Trivy**.
- `fixed/` : la version **corrigée** des 3 fichiers → servira pour la démo « après ».

---

## Partie 3 — Démarrer la stack CI

**Ce qu'on fait :**
```bash
docker compose up -d --build
docker compose ps
```

**Pourquoi `--build` :** l'image Jenkins est **sur-mesure** (on y a ajouté le CLI Docker et Trivy via `ci/jenkins/Dockerfile`), donc Docker doit la construire la 1ʳᵉ fois.

**Les 3 conteneurs et leur rôle :**
| Conteneur | Rôle | Pourquoi |
|---|---|---|
| `jenkins` (:8080) | chef d'orchestre | exécute le pipeline décrit dans le `Jenkinsfile` |
| `sonarqube` (:9000) | analyse le code | détecte les failles **de code** (SAST) |
| `sonar-db` | base PostgreSQL | SonarQube a besoin d'une base pour stocker ses résultats |

📸 **Capture 1** : `docker compose ps` avec les 3 conteneurs « running ».

**Déverrouiller Jenkins (1ʳᵉ fois) :**
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
Ouvre http://localhost:8080, colle le mot de passe, installe les plugins suggérés, crée ton compte admin.

**Pourquoi ce mot de passe caché :** sécurité par défaut de Jenkins — seul quelqu'un qui a accès au serveur (donc toi) peut l'initialiser.

---

## Partie 4 — Connecter Jenkins ↔ SonarQube (l'étape technique)

**Pourquoi cette étape :** Jenkins doit pouvoir **envoyer** le code à SonarQube pour analyse, puis **lire le verdict** (Quality Gate : réussi/échoué). Il faut donc établir une relation de confiance entre les deux via un **token**.

### 4.1 — Générer un token dans SonarQube
**Ce qu'on fait :** http://localhost:9000 (login `admin`/`admin`, change le mot de passe) → clic sur ton avatar → **My Account → Security** → *Generate Tokens* → nom `jenkins-token` → **Generate** → **copie le token** (il ne s'affiche qu'une fois).

**Pourquoi un token (et pas le mot de passe) :** un token est révocable et limité — si Jenkins est compromis, on révoque le token sans changer le compte. Bonne pratique de sécurité.

### 4.2 — Enregistrer le token dans Jenkins
**Ce qu'on fait :** Jenkins → **Manage Jenkins → Credentials** → (global) → **Add Credentials** :
- Kind : **Secret text**
- Secret : *(colle le token SonarQube)*
- ID : `sonar-token`

**Pourquoi :** Jenkins stocke le secret dans son coffre interne. Le `Jenkinsfile` y fera référence par son ID, **sans jamais écrire le token en clair** dans le code (exactement la faille qu'on veut éviter !).

### 4.3 — Déclarer le serveur SonarQube
**Ce qu'on fait :** Jenkins → **Manage Jenkins → System** → section **SonarQube servers** → *Add* :
- Name : `sonarqube`  *(ce nom est utilisé dans le Jenkinsfile : `withSonarQubeEnv('sonarqube')`)*
- Server URL : `http://sonarqube:9000`  *(nom du conteneur sur le réseau Docker)*
- Server authentication token : `sonar-token`

**Pourquoi `http://sonarqube:9000` et pas `localhost` :** à l'intérieur du réseau Docker, les conteneurs s'appellent par leur **nom**, pas par `localhost`. `localhost` depuis Jenkins désignerait Jenkins lui-même.

### 4.4 — Installer le SonarQube Scanner
**Ce qu'on fait :** Jenkins → **Manage Jenkins → Tools** → **SonarQube Scanner** → *Add* → *Install automatically* → dernière version → nomme-le `sonar-scanner`.

**Pourquoi :** le scanner est l'outil qui lit `sonar-project.properties`, empaquette le code et l'envoie à SonarQube.

📸 **Capture 2** : la config du serveur SonarQube dans Jenkins.

---

## Partie 5 — Créer le job pipeline

**Ce qu'on fait :** Jenkins → **New Item** → nom `demo-app-securise` → type **Pipeline** → OK. Dans *Pipeline* :
- Definition : **Pipeline script from SCM**
- SCM : **Git**, URL : `https://github.com/landrysime/03-pipeline-cicd-securise.git`
- Branch : `main`
- Script Path : `Jenkinsfile`
- Save.

**Pourquoi « from SCM » (et pas coller le script) :** le pipeline est **versionné dans le dépôt** (`Jenkinsfile`). C'est le principe « Pipeline as Code » : l'historique Git garde la trace de chaque changement de la chaîne. Plus pro et plus traçable.

---

## Partie 6 — Comprendre le Jenkinsfile (stage par stage)

**Pourquoi lire le pipeline :** c'est le cœur du projet. En entretien, on te demandera d'expliquer ce que fait chaque étape.

| Stage | Ce qu'il fait | Pourquoi |
|---|---|---|
| 1. Checkout | récupère le code | point de départ |
| 2. Tests unitaires | lance `pytest` | on ne sécurise pas du code cassé |
| 3. SAST SonarQube | analyse statique du code | détecte injection, secret en dur… |
| 3b. Quality Gate | lit le verdict SonarQube | **bloque** si le seuil de qualité/sécurité n'est pas atteint |
| 4. SCA Trivy (deps) | scanne les dépendances | détecte les librairies à CVE |
| 5. Build image | construit l'image Docker | prépare le déploiement |
| 6. Scan image Trivy | scanne l'image | détecte les CVE système de l'image de base |
| 7. 🚦 Security Gate | `trivy --exit-code 1` sur CRITICAL | **barrière finale** : refuse une image dangereuse |
| 8. Deploy | lance le conteneur | atteint **seulement si tout est vert** |

**Le point clé :** aux stages 3b, 4 et 7, si une faille dépasse le seuil, la commande renvoie une **erreur** → Jenkins **arrête** le pipeline → **pas de déploiement**. C'est ça, « bloquer automatiquement ».

---

## Partie 7 — Démo « AVANT » : prouver que ça bloque 🔴

**Ce qu'on fait :** le dépôt est en version **vulnérable**. Lance le job : **Build Now**.

**Ce qui doit se passer :** le pipeline **échoue** à une barrière de sécurité (SonarQube Quality Gate FAILED, ou Trivy qui trouve des CVE CRITICAL/HIGH). Le stage **Deploy n'est jamais atteint**.

**Pourquoi c'est la preuve la plus importante :** tu démontres qu'une vraie faille **est stoppée avant la prod**. C'est l'équivalent du « delta Lynis » du projet 02.

📸 **Captures clés :**
- Pipeline **rouge** (vue des stages, barrière en échec).
- SonarQube : tableau des vulnérabilités détectées.
- Trivy : liste des CVE CRITICAL/HIGH.

---

## Partie 8 — Démo « APRÈS » : prouver que le correctif passe 🟢

**Ce qu'on fait :** on applique la version corrigée et on relance.
```bash
cp fixed/app.py app/app.py
cp fixed/requirements.txt app/requirements.txt
cp fixed/Dockerfile app/Dockerfile
git add app/ && git commit -m "fix: correction des vulnerabilites (deps, code, image)"
git push
```
Puis **Build Now**.

**Ce qui doit se passer :** SonarQube Quality Gate **PASSED**, Trivy ne trouve plus de CVE bloquante, le **Security Gate est franchi**, le stage **Deploy** s'exécute.

```bash
curl http://localhost:5000/health      # {"status":"ok"} : l'appli sécurisée tourne
```

**Pourquoi cette bascule rouge → vert est décisive :** elle prouve que la chaîne ne bloque pas « par principe », mais **réagit au risque réel** : elle laisse passer le code sain et arrête le code dangereux.

📸 **Captures :** pipeline **vert** complet, Quality Gate PASSED, `curl /health` qui répond.

---

## Partie 9 — Captures & livrable

**Ce qu'on fait :** tu rassembles tes captures (noms suggérés dans `screenshots/README.md`) et tu me les envoies.

**Ce que je fais ensuite (comme pour le projet 02) :**
- je **renomme** tes captures par étape et je les **pousse** sur GitHub ;
- je rédige le **rapport illustré** (`.docx` + `.pdf`) prêt pour LinkedIn ;
- je génère le **schéma du pipeline** (draw.io).

**Le livrable final :** un dépôt GitHub complet (code + pipeline + preuves + doc) et un rapport PDF racontant le projet du contexte NovaPay jusqu'à la démo avant/après.

---

## Récapitulatif du « pourquoi » en une phrase

> On transforme la sécurité d'un **contrôle manuel ponctuel** en une **barrière automatique à chaque livraison**, et on le **prouve** en montrant une faille bloquée puis débloquée après correction.
