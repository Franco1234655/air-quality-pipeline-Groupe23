import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv()


OUTPUT_DIRECTORY = Path(
    "analysis/figures"
)


def get_connection():

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


def create_visualizations():

    connection = (
        get_connection()
    )

    query = """

        SELECT

            c.city_name,

            f.openweather_aqi,

            f.pm2_5,

            f.pm10

        FROM fact_air_quality AS f

        JOIN dim_city AS c

        ON f.city_id = c.city_id

        ORDER BY c.city_name;

    """

    df = pd.read_sql_query(

        query,

        connection

    )

    connection.close()

    OUTPUT_DIRECTORY.mkdir(

        parents=True,

        exist_ok=True

    )


    # Graphique AQI

    plt.figure(

        figsize=(10, 6)

    )

    plt.bar(

        df["city_name"],

        df["openweather_aqi"]

    )

    plt.title(

        "Indice de qualité de l'air "
        "par ville"

    )

    plt.xlabel(

        "Ville"

    )

    plt.ylabel(

        "Indice OpenWeatherMap"

    )

    plt.tight_layout()

    plt.savefig(

        OUTPUT_DIRECTORY
        / "openweather_aqi_by_city.png"

    )

    plt.close()


    # Graphique PM2.5

    plt.figure(

        figsize=(10, 6)

    )

    plt.bar(

        df["city_name"],

        df["pm2_5"]

    )

    plt.title(

        "Concentration de PM2.5 "
        "par ville"

    )

    plt.xlabel(

        "Ville"

    )

    plt.ylabel(

        "PM2.5"

    )

    plt.tight_layout()

    plt.savefig(

        OUTPUT_DIRECTORY
        / "pm2_5_by_city.png"

    )

    plt.close()


    # Graphique PM10

    plt.figure(

        figsize=(10, 6)

    )

    plt.bar(

        df["city_name"],

        df["pm10"]

    )

    plt.title(

        "Concentration de PM10 "
        "par ville"

    )

    plt.xlabel(

        "Ville"

    )

    plt.ylabel(

        "PM10"

    )

    plt.tight_layout()

    plt.savefig(

        OUTPUT_DIRECTORY
        / "pm10_by_city.png"

    )

    plt.close()


    print(
        "✅ Graphiques créés dans "
        "analysis/figures/"
    )


if __name__ == "__main__":

    create_visualizations()
