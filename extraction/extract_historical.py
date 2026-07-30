import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


# ==========================================
# CHARGEMENT DU FICHIER .env
# ==========================================

load_dotenv()


# ==========================================
# CONFIGURATION DES VILLES
# ==========================================

CITIES = {
    "Antananarivo": {
        "country": "Madagascar",
        "latitude": -18.8792,
        "longitude": 47.5079,
    },
    "Paris": {
        "country": "France",
        "latitude": 48.8566,
        "longitude": 2.3522,
    },
    "Tokyo": {
        "country": "Japon",
        "latitude": 35.6762,
        "longitude": 139.6503,
    },
    "New York": {
        "country": "États-Unis",
        "latitude": 40.7128,
        "longitude": -74.0060,
    },
    "Madrid": {
        "country": "Espagne",
        "latitude": 40.4168,
        "longitude": -3.7038,
    },
}


# ==========================================
# API OPENWEATHERMAP
# ==========================================

HISTORICAL_API_URL = (
    "https://api.openweathermap.org/"
    "data/2.5/air_pollution/history"
)


# ==========================================
# CONFIGURATION DE L'HISTORIQUE
# ==========================================

# Nombre de jours historiques demandé.
# 92 jours est environ égal à 3 mois.

HISTORICAL_DAYS = 365


# ==========================================
# CONVERTIR L'AQI EN TEXTE
# ==========================================

def get_air_quality_level(aqi):

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


# ==========================================
# RÉCUPÉRER L'HISTORIQUE D'UNE VILLE
# ==========================================

def get_historical_data(
    city_name,
    city_info,
    api_key,
    start_timestamp,
    end_timestamp
):

    params = {

        "lat": city_info["latitude"],

        "lon": city_info["longitude"],

        "start": start_timestamp,

        "end": end_timestamp,

        "appid": api_key,

    }

    print(
        f"📡 Récupération de "
        f"{city_name}..."
    )

    try:

        response = requests.get(

            HISTORICAL_API_URL,

            params=params,

            timeout=60

        )

        response.raise_for_status()

        api_data = (
            response.json()
        )

        measurements = (
            api_data.get(
                "list",
                []
            )
        )

        results = []

        for measurement in measurements:

            components = (

                measurement.get(
                    "components",
                    {}
                )

            )

            aqi = (

                measurement.get(
                    "main",
                    {}
                ).get(
                    "aqi"
                )

            )

            measurement_timestamp = (

                measurement.get(
                    "dt"
                )

            )

            measurement_time = (

                datetime.fromtimestamp(

                    measurement_timestamp,

                    tz=timezone.utc

                ).isoformat()

            )

            result = {

                "city": city_name,

                "country": (
                    city_info[
                        "country"
                    ]
                ),

                "latitude": (
                    city_info[
                        "latitude"
                    ]
                ),

                "longitude": (
                    city_info[
                        "longitude"
                    ]
                ),

                "measurement_time": (
                    measurement_time
                ),

                "openweather_aqi": (
                    aqi
                ),

                "pm2_5": (
                    components.get(
                        "pm2_5"
                    )
                ),

                "pm10": (
                    components.get(
                        "pm10"
                    )
                ),

                "carbon_monoxide": (
                    components.get(
                        "co"
                    )
                ),

                "nitrogen_dioxide": (
                    components.get(
                        "no2"
                    )
                ),

                "sulphur_dioxide": (
                    components.get(
                        "so2"
                    )
                ),

                "ozone": (
                    components.get(
                        "o3"
                    )
                ),

                "ammonia": (
                    components.get(
                        "nh3"
                    )
                ),

                "air_quality_level": (
                    get_air_quality_level(
                        aqi
                    )
                ),

                "extracted_at": (

                    datetime.now(

                        timezone.utc

                    ).isoformat()

                ),

            }

            results.append(
                result
            )

        print(

            f"✅ {city_name} : "

            f"{len(results)} "

            "mesure(s) récupérée(s)"

        )

        return results


    except requests.HTTPError:

        print(

            f"❌ Erreur HTTP pour "

            f"{city_name} : "

            f"{response.status_code}"

        )

        print(

            response.text

        )

        return []


    except requests.RequestException as error:

        print(

            f"❌ Erreur réseau pour "

            f"{city_name} : "

            f"{error}"

        )

        return []


# ==========================================
# EXTRACTION DES CINQ VILLES
# ==========================================

def extract_historical_data():

    api_key = os.getenv(

        "OPENWEATHER_API_KEY"

    )

    if not api_key:

        raise ValueError(

            "❌ OPENWEATHER_API_KEY "

            "est absent du fichier .env"

        )


    # Date de fin : maintenant

    end_date = (

        datetime.now(

            timezone.utc

        )

    )


    # Date de début : environ 3 mois avant

    start_date = (

        end_date

        - timedelta(

            days=HISTORICAL_DAYS

        )

    )


    # Conversion en timestamps Unix UTC

    start_timestamp = int(

        start_date.timestamp()

    )


    end_timestamp = int(

        end_date.timestamp()

    )


    print()

    print(

        "===== EXTRACTION "

        "HISTORIQUE ====="

    )

    print(

        f"📅 Début : "

        f"{start_date.isoformat()}"

    )

    print(

        f"📅 Fin : "

        f"{end_date.isoformat()}"

    )

    print(

        f"📆 Durée : "

        f"{HISTORICAL_DAYS} jours"

    )

    print()


    all_results = []


    for (

        city_name,

        city_info

    ) in CITIES.items():

        city_results = (

            get_historical_data(

                city_name,

                city_info,

                api_key,

                start_timestamp,

                end_timestamp

            )

        )

        all_results.extend(

            city_results

        )


    # ======================================
    # CRÉATION DU DOSSIER
    # ======================================

    output_directory = Path(

        "storage/raw"

    )

    output_directory.mkdir(

        parents=True,

        exist_ok=True

    )


    # ======================================
    # NOM DU FICHIER
    # ======================================

    start_name = (

        start_date.strftime(

            "%Y-%m-%d"

        )

    )


    end_name = (

        end_date.strftime(

            "%Y-%m-%d"

        )

    )


    output_file = (

        output_directory

        / (

            "openweather_historical_"

            f"{start_name}_"

            f"to_{end_name}.json"

        )

    )


    # ======================================
    # ENREGISTREMENT JSON
    # ======================================

    with open(

        output_file,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            all_results,

            file,

            ensure_ascii=False,

            indent=4

        )


    print()

    print(

        "================================"

    )

    print(

        "✅ EXTRACTION TERMINÉE"

    )

    print(

        f"🏙️ Villes : "

        f"{len(CITIES)}"

    )

    print(

        f"📊 Mesures totales : "

        f"{len(all_results)}"

    )

    print(

        f"📁 Fichier créé : "

        f"{output_file}"

    )

    print(

        "================================"

    )


if __name__ == "__main__":

    extract_historical_data()
