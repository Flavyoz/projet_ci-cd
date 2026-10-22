"""Point d'entrée : python -m pipeline.main <generer|deposer|creer-tables|traiter>"""

import logging
import sys
from pathlib import Path

import psycopg
from botocore.exceptions import BotoCoreError, ClientError

from pipeline import base_de_donnees, s3
from pipeline.chargement import charger_depuis_s3
from pipeline.generate import generer_csv
from pipeline.retry import PanneSimulee, avec_retry
from pipeline.traitement import traiter

DOSSIER_CSV = Path("data")
log = logging.getLogger("pipeline")


def generer():
    for chemin in generer_csv(DOSSIER_CSV):
        log.info("CSV généré : %s", chemin)


def deposer():
    client = s3.client_s3()
    s3.creer_bucket(client)
    for chemin in sorted(DOSSIER_CSV.glob("*.csv")):
        s3.deposer_fichier(client, chemin)
        log.info("déposé dans le S3 : %s", chemin.name)


def traiter_fichiers():
    client = s3.client_s3()
    for nom in s3.lister_csv(client):
        if base_de_donnees.deja_traite(nom):
            log.info("%s : déjà traité, ignoré", nom)
            continue

        transactions = avec_retry(
            lambda: charger_depuis_s3(client, nom),
            erreurs=(PanneSimulee, BotoCoreError, ClientError),
        )
        resultats = traiter(transactions)
        avec_retry(
            lambda: base_de_donnees.inserer_resultats(nom, transactions, resultats),
            erreurs=(PanneSimulee, psycopg.OperationalError),
        )
        log.info("%s : traité (%d transactions)", nom, len(transactions))


COMMANDES = {
    "generer": generer,
    "deposer": deposer,
    "creer-tables": base_de_donnees.creer_tables,
    "traiter": traiter_fichiers,
}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    COMMANDES[sys.argv[1]]()
