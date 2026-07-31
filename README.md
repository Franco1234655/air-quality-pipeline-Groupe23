# Air Quality Data Pipeline

## Description

Ce projet consiste à concevoir un pipeline de données permettant de collecter, nettoyer, transformer, stocker et analyser des données sur la qualité de l'air dans plusieurs villes.

Les données sont récupérées depuis l'API **OpenWeatherMap**. Le projet utilise des données historiques couvrant une période de **12 mois**, du **30 juillet 2025 au 30 juillet 2026**.

Les villes étudiées sont :

- 🇲🇬 Antananarivo — Madagascar
- 🇫🇷 Paris — France
- 🇯🇵 Tokyo — Japon
- 🇺🇸 New York — États-Unis
- 🇪🇸 Madrid — Espagne

---

## Objectifs

Le projet a pour objectifs de :

- Extraire des données de qualité de l'air depuis l'API OpenWeatherMap ;
- Récupérer les données de cinq villes ;
- Constituer un historique de données sur 12 mois ;
- Stocker les données brutes au format JSON ;
- Nettoyer et transformer les données avec Python ;
- Générer des données préparées au format CSV ;
- Charger les données dans PostgreSQL ;
- Mettre en place un modèle dimensionnel en étoile ;
- Analyser les indicateurs de qualité de l'air ;
- Générer des graphiques de comparaison entre les villes ;
- Versionner le projet avec Git et GitHub.

---

## Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python | Extraction, nettoyage, transformation et analyse |
| OpenWeatherMap API | Source des données de qualité de l'air |
| Pandas | Manipulation et analyse des données |
| PostgreSQL | Data Warehouse |
| SQL | Création des tables et interrogation des données |
| Psycopg2 | Connexion entre Python et PostgreSQL |
| Matplotlib | Création des graphiques |
| Git | Gestion des versions |
| GitHub | Hébergement et collaboration |

---

## Architecture du pipeline

```text
OpenWeatherMap API
        │
        ▼
Extraction avec Python
        │
        ▼
Données brutes JSON
storage/raw/
        │
        ▼
Nettoyage et transformation
avec Python
        │
        ▼
Données préparées CSV
storage/clean/
        │
        ▼
Chargement avec Python
        │
        ▼
PostgreSQL
Data Warehouse
        │
        ▼
Analyse avec Pandas
        │
        ▼
Visualisations avec Matplotlib
Structure du projet
PROJET-DONNEES2/
│
├── README.md
├── architecture.md
├── .gitignore
├── requirements.txt
├── .env
│
├── extraction/
│   ├── extract.py
│   └── extract_historical.py
│
├── transformation/
│   ├── clean.py
│   └── clean_historical.py
│
├── storage/
│   ├── raw/
│   └── clean/
│
├── warehouse/
│   ├── schema.sql
│   └── load.py
│
├── analysis/
│   ├── analyse.py
│   ├── moyenne_pm25_par_ville.png
│   ├── moyenne_pm10_par_ville.png
│   ├── aqi_moyen_par_ville.png
│   └── evolution_mensuelle_pm25.png
│
├── lambda/
│   └── lambda_function.py
│
└── docs/
    └── architecture.png
Données collectées

Les données contiennent notamment les indicateurs suivants :

Indice de qualité de l'air OpenWeatherMap ;
PM2.5 ;
PM10 ;
Monoxyde de carbone ;
Dioxyde d'azote ;
Dioxyde de soufre ;
Ozone ;
Ammoniac ;
Date et heure de la mesure ;
Ville ;
Pays ;
Latitude ;
Longitude.
Période étudiée

Les données historiques couvrent environ 12 mois :

Début : 30 juillet 2025
Fin : 30 juillet 2026
Nombre de villes : 5
Nombre total de mesures : 42 802

Répartition des mesures :

Ville	Nombre de mesures
Antananarivo	8 498
Madrid	8 570
New York	8 570
Paris	8 546
Tokyo	8 618
Modélisation en étoile

Le Data Warehouse utilise une modélisation en étoile.

Tables de dimensions
dim_city

Cette table contient les informations sur les villes :

city_id
city_name
country
latitude
longitude
dim_date

Cette table contient les informations temporelles :

date_id
full_date
day
month
year
quarter
Table de faits
fact_air_quality

Cette table contient les mesures de qualité de l'air :

fact_id
city_id
date_id
measurement_time
openweather_aqi
pm2_5
pm10
carbon_monoxide
nitrogen_dioxide
sulphur_dioxide
ozone
ammonia
air_quality_level
extracted_at

Représentation :

                 dim_city
                     │
                     │
                     ▼
              fact_air_quality
                     ▲
                     │
                     │
                 dim_date
Installation
1. Cloner le dépôt
git clone URL_DU_DEPOT

Entrer dans le dossier :

cd PROJET-DONNEES2
2. Créer l'environnement virtuel
python3 -m venv venv
3. Activer l'environnement virtuel

Sous Linux :

source venv/bin/activate
4. Installer les dépendances
pip install -r requirements.txt
Configuration

Créer un fichier .env à la racine du projet :

OPENWEATHER_API_KEY=VOTRE_CLE_API

DB_HOST=localhost
DB_PORT=5432
DB_NAME=air_quality
DB_USER=air_quality_user
DB_PASSWORD=VOTRE_MOT_DE_PASSE

Le fichier .env ne doit jamais être envoyé sur GitHub.

Exécution du pipeline
1. Extraction des données historiques
python extraction/extract_historical.py

Le fichier JSON est créé dans :

storage/raw/
2. Nettoyage des données historiques
python transformation/clean_historical.py

Le fichier CSV est créé dans :

storage/clean/
3. Création du schéma PostgreSQL
psql -h localhost -U air_quality_user -d air_quality -f warehouse/schema.sql
4. Chargement dans PostgreSQL
python warehouse/load.py
5. Analyse et création des graphiques
python analysis/analyse.py

Les graphiques sont enregistrés dans :

analysis/
Résultats de l'analyse

Moyennes calculées sur les données disponibles :

Ville	PM2.5 moyen	PM10 moyen	AQI moyen
Tokyo	7,48	12,37	2,30
New York	6,66	8,92	1,94
Paris	4,86	6,72	1,73
Madrid	4,52	8,41	1,79
Antananarivo	3,34	5,29	1,14

Selon les données analysées :

Antananarivo possède les moyennes les plus faibles pour les indicateurs affichés ;
Tokyo possède les moyennes les plus élevées pour PM2.5, PM10 et l'indice AQI moyen ;
Les résultats correspondent aux données récupérées depuis OpenWeatherMap pendant la période étudiée.

Ces résultats ne représentent pas nécessairement un classement général définitif de la qualité de l'air dans ces villes.

Visualisations

Le projet génère les graphiques suivants :

Moyenne de PM2.5 par ville ;
Moyenne de PM10 par ville ;
AQI moyen par ville ;
Évolution mensuelle moyenne de PM2.5.
Moyenne de PM2.5

Moyenne de PM10

AQI moyen

Évolution mensuelle de PM2.5

Améliorations futures

Les améliorations possibles sont :

Déployer l'extraction automatique avec AWS Lambda ;
Stocker les données brutes dans AWS S3 ;
Planifier l'exécution automatique du pipeline ;
Utiliser Apache Airflow pour l'orchestration ;
Ajouter d'autres villes ;
Ajouter davantage d'indicateurs ;
Créer un tableau de bord interactif ;
Utiliser les données dans un projet d'intelligence artificielle.
Auteur

Projet réalisé dans le cadre du cours Données 2.


Ensuite, enregistre le fichier puis vérifie son contenu :

```bash
cat README.md

Après cela, vérifie que Git ne détecte pas ton fichier .env :

git status

Si .env n’apparaît pas, tu peux faire :

git add README.md requirements.txt analysis/*.png
git commit -m "Mise à jour du README et ajout des résultats d'analyse"
git push origin main
