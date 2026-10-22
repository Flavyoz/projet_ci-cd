"""Base PostgreSQL : création des tables et insertion des résultats."""

import os
from pathlib import Path

import psycopg

from pipeline.retry import simuler_panne

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://pipeline:pipeline@localhost:5432/transactions")


def connexion():
    return psycopg.connect(DATABASE_URL, autocommit=True)


def creer_tables() -> None:
    with connexion() as conn:
        conn.execute(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))


def deja_traite(nom_fichier: str) -> bool:
    with connexion() as conn:
        ligne = conn.execute("SELECT 1 FROM fichiers_traites WHERE nom_fichier = %s", (nom_fichier,)).fetchone()
    return ligne is not None


def ajouter_totaux(conn, table: str, colonne: str, totaux: dict) -> None:
    # Si la clé existe déjà (fichier précédent), on ajoute au total existant
    for cle, montant in totaux.items():
        conn.execute(
            f"INSERT INTO {table} ({colonne}, total) VALUES (%s, %s) "
            f"ON CONFLICT ({colonne}) DO UPDATE SET total = {table}.total + EXCLUDED.total",
            (cle, montant),
        )


def inserer_resultats(nom_fichier: str, transactions: list[dict], resultats: dict) -> None:
    """Tout est inséré dans UNE transaction SQL : si une erreur arrive, rien n'est enregistré.
    On peut donc réessayer sans risque de compter deux fois."""
    with connexion() as conn, conn.transaction():
        conn.execute("INSERT INTO fichiers_traites (nom_fichier) VALUES (%s)", (nom_fichier,))
        for tx in transactions:
            conn.execute(
                "INSERT INTO transactions VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    tx["transaction_id"], tx["datetime_transaction"], tx["iban_origine"],
                    tx["pays_source"], tx["banque_source"], tx["iban_destinataire"],
                    tx["pays_destinataire"], tx["montant"], resultats["flags"][tx["transaction_id"]],
                    nom_fichier,
                ),
            )
        ajouter_totaux(conn, "somme_envoyee_par_iban", "iban", resultats["envoye_par_iban"])
        ajouter_totaux(conn, "somme_envoyee_par_banque", "banque", resultats["envoye_par_banque"])
        ajouter_totaux(conn, "somme_recue_par_iban", "iban", resultats["recu_par_iban"])

        # Panne simulée APRÈS les écritures et AVANT le commit : la transaction est annulée
        simuler_panne("insertion")
