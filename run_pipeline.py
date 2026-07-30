import subprocess
import sys


STEPS = [

    "extraction/extract.py",

    "transformation/clean.py",

    "warehouse/load.py",

    "analysis/analyse.py",

    "analysis/visualize.py"

]


def run_pipeline():

    for step in STEPS:

        print(
            "\n"
            + "=" * 60
        )

        print(
            f"▶ Exécution : {step}"
        )

        print(
            "=" * 60
        )

        result = subprocess.run(

            [
                sys.executable,
                step
            ]

        )

        if result.returncode != 0:

            print(

                f"❌ Échec de : "
                f"{step}"

            )

            sys.exit(

                result.returncode

            )

    print(

        "\n🎉 Pipeline terminé "
        "avec succès"

    )


if __name__ == "__main__":

    run_pipeline()
