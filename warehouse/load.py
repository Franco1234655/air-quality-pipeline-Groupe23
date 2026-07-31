import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv


# Charger les variables du fichier .env
load_dotenv()


# Dossier contenant les fichiers CSV nettoyés
CLEAN_DIRECTORY = Path("storage/clean")


def get_latest_csv():
    """
    Retourne le fichier CSV actuel OpenWeatherMap
    le plus récent.

    Les fichiers historiques sont volontairement
    exclus du pipeline automatique.
    """

    csv_files = sorted(
        CLEAN_DIRECTORY.glob(
            "openweather_air_quality_clean_*.csv"
        )
    )

    if not csv_files:

        raise FileNotFoundError(
            "Aucun fichier CSV actuel OpenWeatherMap "
            "trouvé dans storage/clean/"
        )

    return csv_files[-1]


def get_database_connection():
    """
    Crée et retourne une connexion PostgreSQL.
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


def create_date_id(date_value):
    """
    Transforme une date en identifiant au format :
    YYYYMMDD.

    Exemple :
    2026-07-31 devient 20260731.
    """

    return int(
        date_value.strftime(
            "%Y%m%d"
        )
    )


def load_air_quality_data():
    """
    Charge les données actuelles OpenWeatherMap
    nettoyées dans PostgreSQL.
    """

    csv_file = get_latest_csv()

    print(
        f"📥 Lecture du fichier : "
        f"{csv_file}"
    )

    # Lire le fichier CSV
    df = pd.read_csv(
        csv_file
    )

    if df.empty:

        print(
            "⚠️ Le fichier CSV est vide."
        )

        return

    # Convertir les colonnes de date
    df["measurement_time"] = (
        pd.to_datetime(
            df["measurement_time"],
            utc=True
        )
    )

    df["extracted_at"] = (
        pd.to_datetime(
            df["extracted_at"],
            utc=True
        )
    )

    # Connexion PostgreSQL
    connection = (
        get_database_connection()
    )

    cursor = (
        connection.cursor()
    )

    inserted_measurements = 0
    existing_measurements = 0

    try:

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

                    float(
                        row["latitude"]
                    ),

                    float(
                        row["longitude"]
                    )

                )
            )

            city_id = (
                cursor.fetchone()[0]
            )


            # ==================================
            # DIMENSION DATE
            # ==================================

            measurement_time = (
                row[
                    "measurement_time"
                ]
            )

            measurement_date = (
                measurement_time.date()
            )

            date_id = (
                create_date_id(
                    measurement_time
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

                    measurement_time.to_pydatetime(),

                    int(
                        row[
                            "openweather_aqi"
                        ]
                    ),

                    float(
                        row[
                            "pm2_5"
                        ]
                    ),

                    float(
                        row[
                            "pm10"
                        ]
                    ),

                    float(
                        row[
                            "carbon_monoxide"
                        ]
                    ),

                    float(
                        row[
                            "nitrogen_dioxide"
                        ]
                    ),

                    float(
                        row[
                            "sulphur_dioxide"
                        ]
                    ),

                    float(
                        row[
                            "ozone"
                        ]
                    ),

                    float(
                        row[
                            "ammonia"
                        ]
                    ),

                    row[
                        "air_quality_level"
                    ],

                    row[
                        "extracted_at"
                    ].to_pydatetime()

                )
            )

            result = (
                cursor.fetchone()
            )

            if result is None:

                existing_measurements += 1

            else:

                inserted_measurements += 1


        # Enregistrer les modifications
        connection.commit()

        print(
            "\n✅ Chargement PostgreSQL terminé"
        )

        print(
            f"📊 Mesures lues : "
            f"{len(df)}"
        )

        print(
            f"➕ Nouvelles mesures insérées : "
            f"{inserted_measurements}"
        )

        print(
            f"⏭️ Mesures déjà présentes : "
            f"{existing_measurements}"
        )


    except Exception as error:

        # Annuler les modifications
        connection.rollback()

        print(
            f"\n❌ Erreur lors du chargement : "
            f"{error}"
        )

        raise


    finally:

        cursor.close()

        connection.close()

        print(
            "🔌 Connexion PostgreSQL fermée"
        )


if __name__ == "__main__":

    load_air_quality_data()