import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv


# ==========================================
# CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
# ==========================================

load_dotenv()


# ==========================================
# DOSSIER DES DONNÉES TRAITÉES
# ==========================================

PROCESSED_DIRECTORY = Path(
    "storage/processed"
)


# ==========================================
# RÉCUPÉRER LE FICHIER CSV LE PLUS RÉCENT
# ==========================================

def get_latest_csv():
    """
    Retourne le fichier CSV OpenWeatherMap
    nettoyé le plus récent.
    """

    csv_files = sorted(
    list(
        PROCESSED_DIRECTORY.glob(
            "openweather_air_quality_clean_*.csv"
        )
    )
    +
    list(
        PROCESSED_DIRECTORY.glob(
            "openweather_historical_clean_*.csv"
        )
    )
)

    if not csv_files:

        raise FileNotFoundError(
            "❌ Aucun fichier CSV OpenWeatherMap "
            "trouvé dans storage/processed/"
        )

    return csv_files[-1]


# ==========================================
# CONNEXION À POSTGRESQL
# ==========================================

def get_database_connection():
    """
    Crée et retourne une connexion
    à la base de données PostgreSQL.
    """

    return psycopg2.connect(

        host=os.getenv(
            "DB_HOST",
            "localhost"
        ),

        port=os.getenv(
            "DB_PORT",
            "5432"
        ),

        database=os.getenv(
            "DB_NAME",
            "air_quality"
        ),

        user=os.getenv(
            "DB_USER",
            "air_quality_user"
        ),

        password=os.getenv(
            "DB_PASSWORD"
        )
    )


# ==========================================
# CRÉER L'IDENTIFIANT DE LA DATE
# ==========================================

def create_date_id(date_value):
    """
    Transforme une date au format :

    YYYY-MM-DD

    en identifiant :

    YYYYMMDD

    Exemple :

    2026-07-30
    devient
    20260730
    """

    return int(
        date_value.strftime(
            "%Y%m%d"
        )
    )


# ==========================================
# CHARGEMENT DES DONNÉES
# ==========================================

def load_air_quality_data():

    # --------------------------------------
    # Récupération du fichier CSV
    # --------------------------------------

    csv_file = (
        get_latest_csv()
    )

    print(
        f"📥 Lecture du fichier : "
        f"{csv_file}"
    )


    # --------------------------------------
    # Lecture du fichier CSV
    # --------------------------------------

    df = pd.read_csv(
        csv_file
    )


    # --------------------------------------
    # Vérification des colonnes obligatoires
    # --------------------------------------

    required_columns = [

        "city",

        "country",

        "latitude",

        "longitude",

        "measurement_time",

        "openweather_aqi",

        "pm2_5",

        "pm10",

        "carbon_monoxide",

        "nitrogen_dioxide",

        "sulphur_dioxide",

        "ozone",

        "ammonia",

        "air_quality_level",

        "extracted_at"

    ]

    missing_columns = [

        column

        for column in required_columns

        if column not in df.columns

    ]

    if missing_columns:

        raise ValueError(

            "❌ Colonnes manquantes dans "
            "le fichier CSV : "

            + ", ".join(
                missing_columns
            )

        )


    # --------------------------------------
    # Conversion des dates
    # --------------------------------------

    df["measurement_time"] = (

        pd.to_datetime(

            df["measurement_time"],

            errors="coerce",

            utc=True

        )

    )


    df["extracted_at"] = (

        pd.to_datetime(

            df["extracted_at"],

            errors="coerce",

            utc=True

        )

    )


    # --------------------------------------
    # Supprimer les lignes avec une date
    # invalide
    # --------------------------------------

    invalid_dates = (

        df["measurement_time"].isna()

        |

        df["extracted_at"].isna()

    )

    if invalid_dates.any():

        print(

            "⚠️ Certaines lignes ont "
            "des dates invalides."

        )

        df = df.loc[
            ~invalid_dates
        ].copy()


    # --------------------------------------
    # Connexion PostgreSQL
    # --------------------------------------

    connection = (
        get_database_connection()
    )

    cursor = (
        connection.cursor()
    )


    # Compteurs

    inserted_count = 0

    duplicate_count = 0


    try:

        # ----------------------------------
        # Parcours des données
        # ----------------------------------

        for _, row in df.iterrows():


            # ==================================
            # DIMENSION VILLE
            # ==================================

            cursor.execute(

                """
                INSERT INTO dim_city (

                    city_name,

                    country,

                    latitude,

                    longitude

                )

                VALUES (

                    %s,

                    %s,

                    %s,

                    %s

                )

                ON CONFLICT (

                    city_name,

                    country

                )

                DO UPDATE SET

                    latitude =
                    EXCLUDED.latitude,

                    longitude =
                    EXCLUDED.longitude

                RETURNING city_id;
                """,

                (

                    row["city"],

                    row["country"],

                    row["latitude"],

                    row["longitude"]

                )

            )


            city_id = (

                cursor.fetchone()[0]

            )


            # ==================================
            # DIMENSION DATE
            # ==================================

            measurement_date = (

                row[
                    "measurement_time"
                ].date()

            )


            date_id = (

                create_date_id(

                    row[
                        "measurement_time"
                    ]

                )

            )


            quarter = (

                (

                    measurement_date.month

                    - 1

                ) // 3

            ) + 1


            cursor.execute(

                """
                INSERT INTO dim_date (

                    date_id,

                    full_date,

                    day,

                    month,

                    year,

                    quarter

                )

                VALUES (

                    %s,

                    %s,

                    %s,

                    %s,

                    %s,

                    %s

                )

                ON CONFLICT (

                    date_id

                )

                DO NOTHING;
                """,

                (

                    date_id,

                    measurement_date,

                    measurement_date.day,

                    measurement_date.month,

                    measurement_date.year,

                    quarter

                )

            )


            # ==================================
            # TABLE DE FAITS
            # ==================================

            cursor.execute(

                """
                INSERT INTO fact_air_quality (

                    city_id,

                    date_id,

                    measurement_time,

                    openweather_aqi,

                    pm2_5,

                    pm10,

                    carbon_monoxide,

                    nitrogen_dioxide,

                    sulphur_dioxide,

                    ozone,

                    ammonia,

                    air_quality_level,

                    extracted_at

                )

                VALUES (

                    %s,

                    %s,

                    %s,

                    %s,

                    %s,

                    %s,

                    %s,

                    %s,

                    %s,

                    %s,

                    %s,

                    %s,

                    %s

                )

                ON CONFLICT (

                    city_id,

                    measurement_time

                )

                DO NOTHING

                RETURNING fact_id;
                """,

                (

                    city_id,

                    date_id,

                    row[
                        "measurement_time"
                    ].to_pydatetime(),

                    int(

                        row[
                            "openweather_aqi"
                        ]

                    ),

                    row["pm2_5"],

                    row["pm10"],

                    row[
                        "carbon_monoxide"
                    ],

                    row[
                        "nitrogen_dioxide"
                    ],

                    row[
                        "sulphur_dioxide"
                    ],

                    row["ozone"],

                    row["ammonia"],

                    row[
                        "air_quality_level"
                    ],

                    row[
                        "extracted_at"
                    ].to_pydatetime()

                )

            )


            # ----------------------------------
            # Vérifier si la mesure a été
            # insérée ou ignorée
            # ----------------------------------

            result = (
                cursor.fetchone()
            )

            if result is None:

                duplicate_count += 1

            else:

                inserted_count += 1


        # --------------------------------------
        # Enregistrer les modifications
        # --------------------------------------

        connection.commit()


        print()

        print(
            "✅ Chargement PostgreSQL "
            "terminé"
        )

        print(
            f"📊 Mesures lues : "
            f"{len(df)}"
        )

        print(
            f"➕ Nouvelles mesures "
            f"insérées : "
            f"{inserted_count}"
        )

        print(
            f"⏭️ Mesures déjà présentes : "
            f"{duplicate_count}"
        )


    except Exception as error:

        # Annuler toutes les opérations
        # en cas d'erreur

        connection.rollback()


        print(

            f"❌ Erreur lors du "
            f"chargement : {error}"

        )


        raise


    finally:

        # --------------------------------------
        # Fermer la connexion
        # --------------------------------------

        cursor.close()

        connection.close()


        print(
            "🔌 Connexion PostgreSQL "
            "fermée"
        )


# ==========================================
# LANCEMENT DU SCRIPT
# ==========================================

if __name__ == "__main__":

    load_air_quality_data()