# Architecture du projet

## Vue générale

Le projet utilise une architecture ETL basée sur les services AWS et PostgreSQL.

```text
                         +----------------------+
                         | API Qualité de l'air |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Python Extraction    |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | AWS Lambda           |
                         | Orchestration        |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | AWS S3               |
                         | Data Lake - Raw      |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Python + SQL         |
                         | Transformation      |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | PostgreSQL           |
                         | Data Warehouse       |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Analyse et           |
                         | Visualisation        |
                         +----------------------+

