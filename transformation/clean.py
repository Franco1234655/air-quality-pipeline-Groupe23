import json
from pathlib import Path

import pandas as pd


RAW_DIRECTORY = Path("storage/raw")
PROCESSED_DIRECTORY = Path("storage/processed")


def get_air_quality_level(aqi):
    """
    Convertit l'indice OpenWeatherMap en niveau lisible.

    Échelle OpenWeatherMap :
    1 = Bonne
    2 = Correcte
    3 = Modérée
    4 = Mauvaise
    5 = Très mauvaise
    """

    if pd.isna(aqi):
        return "Inconnu"

    levels = {
        1: "Bonne",
        2: "Correcte",
        3: "Modérée",
        4: "Mauvaise",
        5: "Très mauvaise",
    }

    return levels.get(
        int(aqi),
        "Inconnu"
    )


def clean_air_quality_data():

    raw_files = sorted(
        RAW_DIRECTORY.glob(
            "openweather_air_quality_*.json"
        )
    )

    if not raw_files:
        print(
            "❌ Aucun fichier OpenWeatherMap "
            "trouvé dans storage/raw/"
        )
        return

    latest_file = raw_files[-1]

    print(
        f"📥 Lecture du fichier : "
        f"{latest_file}"
    )

    with open(
        latest_file,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    df = pd.DataFrame(data)

    print(
        "Nombre de lignes avant "
        f"nettoyage : {len(df)}"
    )

    # Normalisation des noms de colonnes
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Suppression des doublons
    df = df.drop_duplicates()

    # Colonnes numériques
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

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Conversion des dates
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

    # Suppression des lignes sans ville
    df = df.dropna(
        subset=["city"]
    )

    # Niveau de qualité de l'air
    df["air_quality_level"] = (
        df["openweather_aqi"]
        .apply(
            get_air_quality_level
        )
    )

    # Tri des données
    df = df.sort_values(
        by="city"
    )

    print(
        "Nombre de lignes après "
        f"nettoyage : {len(df)}"
    )

    print(
        "\nValeurs manquantes :"
    )

    print(
        df.isna().sum()
    )

    # Création du dossier de sortie
    PROCESSED_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    date_part = (
        latest_file.stem
        .replace(
            "openweather_air_quality_",
            ""
        )
    )

    output_file = (
        PROCESSED_DIRECTORY
        / (
            "openweather_air_quality_clean_"
            f"{date_part}.csv"
        )
    )

    # Enregistrement du CSV
    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    print(
        "\n✅ Transformation terminée"
    )

    print(
        "📁 Fichier propre créé : "
        f"{output_file}"
    )

    print(
        "\nAperçu des données :"
    )

    print(
        df.head()
    )


if __name__ == "__main__":

    clean_air_quality_data()