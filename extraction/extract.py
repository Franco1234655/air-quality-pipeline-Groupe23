import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


# Chargement des variables du fichier .env
load_dotenv()


# Les cinq villes étudiées
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


API_URL = "https://api.openweathermap.org/data/2.5/air_pollution"


def get_air_quality(
    city_name,
    city_info,
    api_key
):
    """
    Récupère les données actuelles de qualité
    de l'air pour une ville avec OpenWeatherMap.
    """

    params = {
        "lat": city_info["latitude"],
        "lon": city_info["longitude"],
        "appid": api_key,
    }

    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        api_data = response.json()

        # OpenWeatherMap renvoie les mesures
        # dans le premier élément de "list"
        air_data = api_data["list"][0]

        components = (
            air_data.get(
                "components",
                {}
            )
        )

        measurement_timestamp = (
            air_data.get("dt")
        )

        measurement_time = (
            datetime.fromtimestamp(
                measurement_timestamp,
                tz=timezone.utc
            ).isoformat()
        )

        result = {
            "city": city_name,
            "country": city_info["country"],
            "latitude": city_info["latitude"],
            "longitude": city_info["longitude"],

            "measurement_time": (
                measurement_time
            ),

            # Indice AQI OpenWeatherMap :
            # 1 = bon
            # 2 = correct
            # 3 = modéré
            # 4 = mauvais
            # 5 = très mauvais
            "openweather_aqi": (
                air_data
                .get(
                    "main",
                    {}
                )
                .get("aqi")
            ),

            "pm2_5": (
                components
                .get("pm2_5")
            ),

            "pm10": (
                components
                .get("pm10")
            ),

            "carbon_monoxide": (
                components
                .get("co")
            ),

            "nitrogen_dioxide": (
                components
                .get("no2")
            ),

            "sulphur_dioxide": (
                components
                .get("so2")
            ),

            "ozone": (
                components
                .get("o3")
            ),

            "ammonia": (
                components
                .get("nh3")
            ),

            "extracted_at": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
        }

        print(
            f"✅ Données récupérées : "
            f"{city_name}"
        )

        return result

    except requests.RequestException as error:

        print(
            f"❌ Erreur pour "
            f"{city_name} : {error}"
        )

        return None

    except (
        KeyError,
        IndexError,
        TypeError
    ) as error:

        print(
            f"❌ Réponse inattendue pour "
            f"{city_name} : {error}"
        )

        return None


def extract_all_cities():
    """
    Extrait les données des cinq villes
    et les enregistre dans un fichier JSON.
    """

    api_key = os.getenv(
        "OPENWEATHER_API_KEY"
    )

    if not api_key:

        raise ValueError(
            "La variable "
            "OPENWEATHER_API_KEY "
            "est absente du fichier .env"
        )

    results = []

    for (
        city_name,
        city_info
    ) in CITIES.items():

        city_data = get_air_quality(
            city_name,
            city_info,
            api_key
        )

        if city_data is not None:

            results.append(
                city_data
            )

    output_directory = Path(
        "storage/raw"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    current_date = (
        datetime.now(
            timezone.utc
        )
        .strftime("%Y-%m-%d")
    )

    output_file = (
        output_directory
        / (
            "openweather_air_quality_"
            f"{current_date}.json"
        )
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(
        "\n✅ Extraction terminée : "
        f"{len(results)} ville(s)"
    )

    print(
        "📁 Fichier créé : "
        f"{output_file}"
    )

    return results


if __name__ == "__main__":

    extract_all_cities()
