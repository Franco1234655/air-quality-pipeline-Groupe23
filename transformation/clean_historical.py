import json
from pathlib import Path

import pandas as pd


# ==========================================
# DOSSIERS
# ==========================================

RAW_DIRECTORY = Path(
    "storage/raw"
)

PROCESSED_DIRECTORY = Path(
    "storage/processed"
)


# ==========================================
# TROUVER LE FICHIER HISTORIQUE
# ==========================================

def get_latest_historical_file():

    files = sorted(
        RAW_DIRECTORY.glob(
            "openweather_historical_*.json"
        )
    )

    if not files:

        raise FileNotFoundError(
            "Aucun fichier historique "
            "OpenWeatherMap trouvé dans "
            "storage/raw/"
        )

    return files[-1]


# ==========================================
# NETTOYAGE DES DONNÉES
# ==========================================

def clean_historical_data():

    input_file = (
        get_latest_historical_file()
    )

    print(
        f"📥 Lecture du fichier : "
        f"{input_file}"
    )

    # Lecture du fichier JSON

    with open(
        input_file,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(
            file
        )

    # Conversion en DataFrame

    df = pd.DataFrame(
        data
    )

    print(
        f"📊 Mesures brutes : "
        f"{len(df)}"
    )

    print(
        f"📋 Colonnes trouvées : "
        f"{len(df.columns)}"
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

        utc=True,

        errors="coerce"

    )


    df[
        "extracted_at"
    ] = pd.to_datetime(

        df[
            "extracted_at"
        ],

        utc=True,

        errors="coerce"

    )


    # ======================================
    # CONVERSION DES COLONNES NUMÉRIQUES
    # ======================================

    numeric_columns = [

        "latitude",

        "longitude",

        "openweather_aqi",

        "pm2_5",

        "pm10",

        "carbon_monoxide",

        "nitrogen_dioxide",

        "sulphur_dioxide",

        "ozone",

        "ammonia",

    ]


    for column in numeric_columns:

        if column in df.columns:

            df[column] = (
                pd.to_numeric(

                    df[column],

                    errors="coerce"

                )
            )


    # ======================================
    # SUPPRESSION DES LIGNES INCOMPLÈTES
    # ======================================

    required_columns = [

        "city",

        "country",

        "latitude",

        "longitude",

        "measurement_time",

        "openweather_aqi",

    ]


    before_missing = len(
        df
    )


    df = df.dropna(

        subset=required_columns

    )


    removed_missing = (

        before_missing

        - len(df)

    )


    print(

        f"🧹 Lignes supprimées "

        f"à cause de valeurs "

        f"manquantes : "

        f"{removed_missing}"

    )


    # ======================================
    # SUPPRESSION DES DOUBLONS
    # ======================================

    before_duplicates = len(
        df
    )


    df = df.drop_duplicates(

        subset=[

            "city",

            "measurement_time"

        ],

        keep="last"

    )


    removed_duplicates = (

        before_duplicates

        - len(df)

    )


    print(

        f"🔁 Doublons supprimés : "

        f"{removed_duplicates}"

    )


    # ======================================
    # TRI DES DONNÉES
    # ======================================

    df = df.sort_values(

        by=[

            "city",

            "measurement_time"

        ]

    )


    # ======================================
    # RÉORGANISATION DES COLONNES
    # ======================================

    output_columns = [

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

        "extracted_at",

    ]


    existing_columns = [

        column

        for column

        in output_columns

        if column in df.columns

    ]


    df = df[

        existing_columns

    ]


    # ======================================
    # CRÉATION DU DOSSIER DE SORTIE
    # ======================================

    PROCESSED_DIRECTORY.mkdir(

        parents=True,

        exist_ok=True

    )


    # ======================================
    # NOM DU FICHIER CSV
    # ======================================

    input_name = (

        input_file.stem

    )


    output_name = (

        input_name.replace(

            "openweather_historical_",

            "openweather_historical_clean_"

        )

        + ".csv"

    )


    output_file = (

        PROCESSED_DIRECTORY

        / output_name

    )


    # ======================================
    # ENREGISTREMENT DU CSV
    # ======================================

    df.to_csv(

        output_file,

        index=False,

        encoding="utf-8"

    )


    # ======================================
    # RÉSUMÉ
    # ======================================

    print()

    print(

        "================================"

    )

    print(

        "✅ NETTOYAGE TERMINÉ"

    )

    print(

        f"📊 Mesures finales : "

        f"{len(df)}"

    )

    print(

        f"🏙️ Nombre de villes : "

        f"{df['city'].nunique()}"

    )

    print(

        f"📅 Première mesure : "

        f"{df['measurement_time'].min()}"

    )

    print(

        f"📅 Dernière mesure : "

        f"{df['measurement_time'].max()}"

    )

    print(

        f"📁 Fichier CSV créé : "

        f"{output_file}"

    )

    print(

        "================================"

    )


if __name__ == "__main__":

    clean_historical_data()
