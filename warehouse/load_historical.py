import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv


# ==========================================
# CHARGEMENT DES VARIABLES .env
# ==========================================

load_dotenv()


# ==========================================
# DOSSIER DES DONNÉES TRAITÉES
# ==========================================

PROCESSED_DIRECTORY = Path(
    "storage/clean"
)


# ==========================================
# RECHERCHER LE FICHIER HISTORIQUE
# ==========================================

def get_latest_historical_csv():

    csv_files = sorted(

        PROCESSED_DIRECTORY.glob(

            "openweather_historical_clean_*.csv"

        )

    )

    if not csv_files:

        raise FileNotFoundError(

            "Aucun fichier CSV historique "

            "trouvé dans storage/clean/"

        )

    return csv_files[-1]


# ==========================================
# CONNEXION POSTGRESQL
# ==========================================

def get_database_connection():

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
# CRÉATION DE L'IDENTIFIANT DE DATE
# ==========================================

def create_date_id(

    date_value

):

    return int(

        date_value.strftime(

            "%Y%m%d"

        )

    )


# ==========================================
# CHARGEMENT DES DONNÉES
# ==========================================

def load_historical_data():

    csv_file = (

        get_latest_historical_csv()

    )

    print(

        f"📥 Lecture du fichier : "

        f"{csv_file}"

    )


    # ======================================
    # LECTURE DU CSV
    # ======================================

    df = pd.read_csv(

        csv_file

    )


    print(

        f"📊 Mesures à charger : "

        f"{len(df)}"

    )


    # ======================================
    # CONVERSION DES DATES
    # ======================================

    df[

        "measurement_time"

    ] = pd.to_datetime(

        df[

            "measurement_time"

        ],

        utc=True

    )


    df[

        "extracted_at"

    ] = pd.to_datetime(

        df[

            "extracted_at"

        ],

        utc=True

    )


    # ======================================
    # CONNEXION À POSTGRESQL
    # ======================================

    connection = (

        get_database_connection()

    )

    cursor = (

        connection.cursor()

    )


    inserted_count = 0

    skipped_count = 0


    try:

        # ==================================
        # BOUCLE SUR LES MESURES
        # ==================================

        for index, row in df.iterrows():

            # ==============================
            # DIMENSION VILLE
            # ==============================

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

                    row[

                        "city"

                    ],

                    row[

                        "country"

                    ],

                    row[

                        "latitude"

                    ],

                    row[

                        "longitude"

                    ]

                )

            )


            city_id = (

                cursor.fetchone()[0]

            )


            # ==============================
            # DIMENSION DATE
            # ==============================

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


            # ==============================
            # TABLE DE FAITS
            # ==============================

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

                    row[

                        "pm2_5"

                    ],

                    row[

                        "pm10"

                    ],

                    row[

                        "carbon_monoxide"

                    ],

                    row[

                        "nitrogen_dioxide"

                    ],

                    row[

                        "sulphur_dioxide"

                    ],

                    row[

                        "ozone"

                    ],

                    row[

                        "ammonia"

                    ],

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


            if result:

                inserted_count += 1

            else:

                skipped_count += 1


            # ==============================
            # AFFICHAGE DE PROGRESSION
            # ==============================

            if (

                (index + 1)

                % 1000

                == 0

            ):

                connection.commit()

                print(

                    f"⏳ "

                    f"{index + 1}/"

                    f"{len(df)} "

                    "mesures traitées"

                )


        # ==================================
        # VALIDATION FINALE
        # ==================================

        connection.commit()


        print()

        print(

            "================================"

        )

        print(

            "✅ CHARGEMENT HISTORIQUE TERMINÉ"

        )

        print(

            f"📊 Mesures lues : "

            f"{len(df)}"

        )

        print(

            f"➕ Nouvelles mesures insérées : "

            f"{inserted_count}"

        )

        print(

            f"⏭️ Mesures déjà présentes : "

            f"{skipped_count}"

        )

        print(

            "================================"

        )


    except Exception as error:

        connection.rollback()

        print(

            f"❌ Erreur lors du chargement : "

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

    load_historical_data()
