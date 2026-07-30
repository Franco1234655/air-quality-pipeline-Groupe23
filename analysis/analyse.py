import os

import pandas as pd
import psycopg2
import matplotlib.pyplot as plt

from dotenv import load_dotenv


# ==========================================
# CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
# ==========================================

load_dotenv()


# ==========================================
# CONNEXION À POSTGRESQL
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
# ANALYSE DES DONNÉES
# ==========================================

def analyse_air_quality():

    # ======================================
    # CONNEXION À LA BASE DE DONNÉES
    # ======================================

    connection = (
        get_database_connection()
    )


    # ======================================
    # REQUÊTE SQL
    # ======================================

    query = """

        SELECT

            c.city_name,

            c.country,

            f.measurement_time,

            d.full_date,

            f.openweather_aqi,

            f.pm2_5,

            f.pm10,

            f.carbon_monoxide,

            f.nitrogen_dioxide,

            f.sulphur_dioxide,

            f.ozone,

            f.ammonia,

            f.air_quality_level

        FROM fact_air_quality AS f

        JOIN dim_city AS c

            ON f.city_id = c.city_id

        JOIN dim_date AS d

            ON f.date_id = d.date_id

        ORDER BY

            f.measurement_time,

            c.city_name;

    """


    # ======================================
    # LECTURE DES DONNÉES
    # ======================================

    df = pd.read_sql_query(

        query,

        connection

    )


    # ======================================
    # FERMETURE DE LA CONNEXION
    # ======================================

    connection.close()


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
        "full_date"
    ] = pd.to_datetime(

        df[
            "full_date"
        ],

        errors="coerce"

    )


    # ======================================
    # INFORMATIONS GÉNÉRALES
    # ======================================

    print(
        "\n================================"
    )

    print(
        "📊 ANALYSE DE LA QUALITÉ DE L'AIR"
    )

    print(
        "================================"
    )


    print(

        f"\n📊 Nombre total de mesures : "

        f"{len(df)}"

    )


    print(

        f"🏙️ Nombre de villes : "

        f"{df['city_name'].nunique()}"

    )


    print(

        f"📅 Début des données : "

        f"{df['measurement_time'].min()}"

    )


    print(

        f"📅 Fin des données : "

        f"{df['measurement_time'].max()}"

    )


    # ======================================
    # APERÇU DES DONNÉES
    # ======================================

    print(
        "\n===== APERÇU DES 20 PREMIÈRES LIGNES =====\n"
    )


    print(

        df.head(

            20

        ).to_string(

            index=False

        )

    )


    # ======================================
    # STATISTIQUES GÉNÉRALES
    # ======================================

    print(
        "\n===== STATISTIQUES GÉNÉRALES =====\n"
    )


    print(

        df[

            [

                "openweather_aqi",

                "pm2_5",

                "pm10",

                "ozone"

            ]

        ].describe()

    )


    # ======================================
    # AQI MOYEN PAR VILLE
    # ======================================

    print(
        "\n===== AQI MOYEN PAR VILLE =====\n"
    )


    average_aqi = (

        df.groupby(

            "city_name"

        )[

            "openweather_aqi"

        ]

        .mean()

        .sort_values()

    )


    print(

        average_aqi.round(

            2

        )

    )


    # ======================================
    # VILLE AVEC AQI LE PLUS FAIBLE
    # ET LA PLUS ÉLEVÉE
    # ======================================

    if not average_aqi.empty:


        best_city = (

            average_aqi.idxmin()

        )


        worst_city = (

            average_aqi.idxmax()

        )


        print(

            "\n🌿 Ville avec "

            "l'AQI moyen le plus faible : "

            f"{best_city}"

        )


        print(

            "⚠️ Ville avec "

            "l'AQI moyen le plus élevé : "

            f"{worst_city}"

        )


    # ======================================
    # MOYENNES DES POLLUANTS PAR VILLE
    # ======================================

    city_summary = (

        df.groupby(

            "city_name"

        )

        .agg(

            moyenne_pm2_5=(

                "pm2_5",

                "mean"

            ),

            moyenne_pm10=(

                "pm10",

                "mean"

            ),

            aqi_moyen=(

                "openweather_aqi",

                "mean"

            )

        )

        .reset_index()

        .sort_values(

            "moyenne_pm2_5",

            ascending=False

        )

    )


    # ======================================
    # ARRONDIR LES RÉSULTATS
    # ======================================

    city_summary[

        "moyenne_pm2_5"

    ] = (

        city_summary[

            "moyenne_pm2_5"

        ].round(

            2

        )

    )


    city_summary[

        "moyenne_pm10"

    ] = (

        city_summary[

            "moyenne_pm10"

        ].round(

            2

        )

    )


    city_summary[

        "aqi_moyen"

    ] = (

        city_summary[

            "aqi_moyen"

        ].round(

            2

        )

    )


    # ======================================
    # AFFICHAGE DU RÉSUMÉ
    # ======================================

    print(
        "\n===== MOYENNES PAR VILLE =====\n"
    )


    print(

        city_summary.to_string(

            index=False

        )

    )


    # ======================================
    # GRAPHIQUE 1 : PM2.5
    # ======================================

    plt.figure(

        figsize=(10, 6)

    )


    plt.bar(

        city_summary[

            "city_name"

        ],

        city_summary[

            "moyenne_pm2_5"

        ]

    )


    plt.title(

        "Moyenne annuelle de PM2.5 par ville"

    )


    plt.xlabel(

        "Ville"

    )


    plt.ylabel(

        "PM2.5 moyenne"

    )


    plt.xticks(

        rotation=20

    )


    plt.tight_layout()


    plt.savefig(

        "analysis/moyenne_pm25_par_ville.png",

        dpi=300

    )


    plt.close()


    # ======================================
    # GRAPHIQUE 2 : PM10
    # ======================================

    plt.figure(

        figsize=(10, 6)

    )


    plt.bar(

        city_summary[

            "city_name"

        ],

        city_summary[

            "moyenne_pm10"

        ]

    )


    plt.title(

        "Moyenne annuelle de PM10 par ville"

    )


    plt.xlabel(

        "Ville"

    )


    plt.ylabel(

        "PM10 moyenne"

    )


    plt.xticks(

        rotation=20

    )


    plt.tight_layout()


    plt.savefig(

        "analysis/moyenne_pm10_par_ville.png",

        dpi=300

    )


    plt.close()


    # ======================================
    # GRAPHIQUE 3 : AQI MOYEN
    # ======================================

    plt.figure(

        figsize=(10, 6)

    )


    plt.bar(

        city_summary[

            "city_name"

        ],

        city_summary[

            "aqi_moyen"

        ]

    )


    plt.title(

        "AQI moyen OpenWeatherMap par ville"

    )


    plt.xlabel(

        "Ville"

    )


    plt.ylabel(

        "AQI moyen"

    )


    plt.xticks(

        rotation=20

    )


    plt.tight_layout()


    plt.savefig(

        "analysis/aqi_moyen_par_ville.png",

        dpi=300

    )


    plt.close()


    # ======================================
    # PRÉPARATION DES DONNÉES MENSUELLES
    # ======================================

    df[

        "month"

    ] = (

        df[

            "measurement_time"

        ]

        .dt.to_period(

            "M"

        )

        .astype(

            str

        )

    )


    # ======================================
    # MOYENNE MENSUELLE DE PM2.5
    # ======================================

    monthly_pm25 = (

        df.groupby(

            [

                "month",

                "city_name"

            ]

        )[

            "pm2_5"

        ]

        .mean()

        .reset_index()

    )


    # ======================================
    # TABLEAU POUR LE GRAPHIQUE
    # ======================================

    monthly_pivot = (

        monthly_pm25.pivot(

            index="month",

            columns="city_name",

            values="pm2_5"

        )

    )


    # ======================================
    # GRAPHIQUE 4 :
    # ÉVOLUTION MENSUELLE DE PM2.5
    # ======================================

    plt.figure(

        figsize=(13, 7)

    )


    for city in monthly_pivot.columns:


        plt.plot(

            monthly_pivot.index,

            monthly_pivot[

                city

            ],

            marker="o",

            label=city

        )


    plt.title(

        "Évolution mensuelle moyenne de PM2.5"

    )


    plt.xlabel(

        "Mois"

    )


    plt.ylabel(

        "PM2.5 moyenne"

    )


    plt.xticks(

        rotation=45

    )


    plt.legend()


    plt.tight_layout()


    plt.savefig(

        "analysis/evolution_mensuelle_pm25.png",

        dpi=300

    )


    plt.close()


    # ======================================
    # FIN DE L'ANALYSE
    # ======================================

    print(
        "\n================================"
    )

    print(
        "✅ ANALYSE ET VISUALISATION TERMINÉES"
    )

    print(
        "📁 Graphiques enregistrés dans analysis/"
    )

    print(
        "================================\n"
    )


# ==========================================
# LANCEMENT DU PROGRAMME
# ==========================================

if __name__ == "__main__":

    analyse_air_quality()