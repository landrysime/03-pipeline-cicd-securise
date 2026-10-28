# Image Jenkins outillée pour le pipeline DevSecOps :
#   - Jenkins LTS
#   - le CLI Docker (pour builder l'image de l'appli via le socket monté)
#   - Trivy (scan de vulnérabilités : système de fichiers + image)
# Construite automatiquement par docker-compose (service jenkins).
FROM jenkins/jenkins:2.452.3-lts-jdk17

USER root

# --- Docker CLI ---
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl gnupg lsb-release && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
        > /etc/apt/sources.list.d/docker.list && \
    apt-get update && apt-get install -y --no-install-recommends docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

# --- Trivy ---
RUN curl -fsSL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh \
        | sh -s -- -b /usr/local/bin v0.52.2 && \
    trivy --version

# Pré-installer les plugins utiles (évite la configuration manuelle)
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

USER jenkins
