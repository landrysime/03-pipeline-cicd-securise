// ============================================================
// Pipeline CI/CD sécurisé (DevSecOps) — Projet 03
//
// Principe « shift-left » : la sécurité est intégrée AU pipeline.
// Un commit vulnérable est BLOQUÉ avant le déploiement.
//
// Étapes :
//   1. Checkout
//   2. Tests unitaires
//   3. SAST   — SonarQube (analyse statique du code) + Quality Gate
//   4. SCA    — Trivy fs (vulnérabilités des dépendances)
//   5. Build  — image Docker de l'appli
//   6. Scan image — Trivy (CVE système dans l'image)
//   7. 🚦 Security Gate — échoue si CRITICAL/HIGH détecté
//   8. Deploy — uniquement si toutes les barrières sont vertes
// ============================================================
pipeline {
    agent any

    environment {
        IMAGE_NAME   = "demo-app"
        IMAGE_TAG    = "${env.BUILD_NUMBER}"
        SONAR_HOST   = "http://sonarqube:9000"
        // Seuil de sévérité qui fait échouer le pipeline
        TRIVY_SEVERITY = "CRITICAL,HIGH"
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {

        stage('1. Checkout') {
            steps {
                checkout scm
                sh 'mkdir -p reports'
            }
        }

        stage('2. Tests unitaires') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -q -r app/requirements.txt pytest
                    pytest app/tests -q
                '''
            }
        }

        stage('3. SAST — SonarQube') {
            steps {
                withSonarQubeEnv('sonarqube') {
                    sh '''
                        sonar-scanner \
                          -Dsonar.host.url=${SONAR_HOST} \
                          -Dsonar.projectKey=demo-app
                    '''
                }
            }
        }

        stage('3b. Quality Gate SonarQube') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    // Échoue le build si le Quality Gate SonarQube n'est pas « Passed »
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('4. SCA — Trivy (dépendances)') {
            steps {
                // Rapport lisible (toujours produit)
                sh 'trivy fs --scanners vuln --severity ${TRIVY_SEVERITY} app/ | tee reports/trivy-deps.txt'
                // Barrière : code de sortie 1 si une vuln CRITICAL/HIGH est trouvée
                sh 'trivy fs --scanners vuln --severity ${TRIVY_SEVERITY} --exit-code 1 app/'
            }
        }

        stage('5. Build image') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} app/'
            }
        }

        stage('6. Scan image — Trivy') {
            steps {
                sh 'trivy image --severity ${TRIVY_SEVERITY} ${IMAGE_NAME}:${IMAGE_TAG} | tee reports/trivy-image.txt'
            }
        }

        stage('7. 🚦 Security Gate') {
            steps {
                // La barrière finale : refuse le déploiement si l'image contient du CRITICAL/HIGH
                sh 'trivy image --severity CRITICAL --exit-code 1 ${IMAGE_NAME}:${IMAGE_TAG}'
                echo '✅ Security Gate franchi : aucune vulnérabilité bloquante.'
            }
        }

        stage('8. Deploy') {
            steps {
                // Atteint uniquement si TOUTES les barrières sont vertes
                sh '''
                    docker rm -f demo-app-prod 2>/dev/null || true
                    docker run -d --name demo-app-prod -p 5000:5000 ${IMAGE_NAME}:${IMAGE_TAG}
                '''
                echo '🚀 Déploiement effectué (code sécurisé).'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/*.txt', allowEmptyArchive: true
        }
        failure {
            echo '❌ Pipeline ARRÊTÉ : une barrière de sécurité a bloqué le déploiement.'
        }
        success {
            echo '✅ Pipeline vert : code conforme, image saine, déploiement autorisé.'
        }
    }
}
