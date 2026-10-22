"""Chargement des données : télécharge un CSV depuis le S3 et le convertit en liste de transactions."""

import csv
import io
from datetime import datetime
from decimal import Decimal

from pipeline.retry import simuler_panne
from pipeline.s3 import BUCKET


def lire_csv(texte: str) -> list[dict]:
    transactions = list(csv.DictReader(io.StringIO(texte)))
    for tx in transactions:
        tx["datetime_transaction"] = datetime.fromisoformat(tx["datetime_transaction"])
        tx["montant"] = Decimal(tx["montant"])
    return transactions


def charger_depuis_s3(s3, nom_fichier: str) -> list[dict]:
    simuler_panne("telechargement")
    contenu = s3.get_object(Bucket=BUCKET, Key=nom_fichier)["Body"].read()
    return lire_csv(contenu.decode("utf-8"))
