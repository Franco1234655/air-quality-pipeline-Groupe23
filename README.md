# Air Quality Data Pipeline

## Description

Ce projet consiste à concevoir un pipeline de données permettant de collecter, stocker, transformer et analyser des données sur la qualité de l'air dans plusieurs villes.

Les villes étudiées sont :

- Antananarivo — Madagascar
- Paris — France
- Tokyo — Japon
- New York — États-Unis
- Madrid — Espagne

## Objectifs

Le projet a pour objectifs de :

- Extraire des données de qualité de l'air depuis une API ;
- Stocker les données brutes dans AWS S3 ;
- Nettoyer et transformer les données avec Python et SQL ;
- Charger les données préparées dans PostgreSQL ;
- Réaliser une modélisation en étoile et en flocon ;
- Analyser et visualiser les données ;
- Automatiser l'extraction avec AWS Lambda ;
- Versionner le projet avec Git et GitHub.

## Architecture

```text
API de qualité de l'air
          |
          v
Extraction avec Python
          |
          v
AWS Lambda
          |
          v
AWS S3 - Data Lake
          |
          v
Transformation avec Python et SQL
          |
          v
PostgreSQL - Data Warehouse
          |
          v
Analyse et visualisation
