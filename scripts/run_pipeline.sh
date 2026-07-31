#!/usr/bin/env bash

# Arrêter le script dès qu'une commande échoue
set -e

# Récupérer automatiquement le chemin du projet
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Définir le fichier de logs
LOG_FILE="$PROJECT_DIR/logs/pipeline.log"

# Créer le dossier des logs s'il n'existe pas
mkdir -p "$PROJECT_DIR/logs"

# Fonction pour écrire dans le terminal et dans le fichier de logs
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" | tee -a "$LOG_FILE"
}

# Début du pipeline
echo "==================================================" | tee -a "$LOG_FILE"
log_message "DÉBUT DU PIPELINE"

# Aller dans le dossier du projet
cd "$PROJECT_DIR"

# Activer l'environnement virtuel
source "$PROJECT_DIR/venv/bin/activate"

# ==========================================
# ÉTAPE 1 : EXTRACTION DES DONNÉES ACTUELLES
# ==========================================

log_message "Début de l'extraction OpenWeatherMap"

python extraction/extract.py 2>&1 | tee -a "$LOG_FILE"

log_message "Extraction réussie"

# ==========================================
# ÉTAPE 2 : NETTOYAGE DES DONNÉES
# ==========================================

log_message "Début du nettoyage"

python transformation/clean.py 2>&1 | tee -a "$LOG_FILE"

log_message "Nettoyage réussi"

# ==========================================
# ÉTAPE 3 : CHARGEMENT POSTGRESQL
# ==========================================

log_message "Début du chargement PostgreSQL"

python warehouse/load.py 2>&1 | tee -a "$LOG_FILE"

log_message "Chargement PostgreSQL réussi"

# Fin du pipeline
log_message "PIPELINE TERMINÉ AVEC SUCCÈS"
echo "==================================================" | tee -a "$LOG_FILE"
