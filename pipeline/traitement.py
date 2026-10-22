"""Traitements : fonctions PURES (elles ne lisent/n'écrivent rien, même entrée = même sortie)."""

from decimal import Decimal

SEUIL_FLAG = Decimal("5000")


def somme_par(transactions: list[dict], colonne: str) -> dict:
    totaux = {}
    for tx in transactions:
        cle = tx[colonne]
        totaux[cle] = totaux.get(cle, Decimal("0")) + tx["montant"]
    return totaux


def somme_envoyee_par_iban(transactions):
    return somme_par(transactions, "iban_origine")


def somme_envoyee_par_banque(transactions):
    return somme_par(transactions, "banque_source")


def somme_recue_par_iban(transactions):
    return somme_par(transactions, "iban_destinataire")


def est_flaggee(transaction: dict) -> bool:
    """Flag si le montant est AU-DESSUS de 5000 (5000 pile n'est pas flaggé)."""
    return transaction["montant"] > SEUIL_FLAG


def traiter(transactions: list[dict]) -> dict:
    return {
        "envoye_par_iban": somme_envoyee_par_iban(transactions),
        "envoye_par_banque": somme_envoyee_par_banque(transactions),
        "recu_par_iban": somme_recue_par_iban(transactions),
        "flags": {tx["transaction_id"]: est_flaggee(tx) for tx in transactions},
    }
