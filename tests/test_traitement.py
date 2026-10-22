"""Tests unitaires des fonctions de traitement (pas besoin de base ni de S3)."""

from decimal import Decimal

from pipeline.traitement import (
    est_flaggee,
    somme_envoyee_par_banque,
    somme_envoyee_par_iban,
    somme_recue_par_iban,
)

TRANSACTIONS = [
    {"transaction_id": "1", "iban_origine": "A", "banque_source": "X", "iban_destinataire": "B", "montant": Decimal("100")},
    {"transaction_id": "2", "iban_origine": "A", "banque_source": "Y", "iban_destinataire": "C", "montant": Decimal("50.50")},
    {"transaction_id": "3", "iban_origine": "B", "banque_source": "X", "iban_destinataire": "C", "montant": Decimal("10")},
]


def test_somme_envoyee_par_iban():
    assert somme_envoyee_par_iban(TRANSACTIONS) == {"A": Decimal("150.50"), "B": Decimal("10")}


def test_somme_envoyee_par_banque():
    assert somme_envoyee_par_banque(TRANSACTIONS) == {"X": Decimal("110"), "Y": Decimal("50.50")}


def test_somme_recue_par_iban():
    assert somme_recue_par_iban(TRANSACTIONS) == {"B": Decimal("100"), "C": Decimal("60.50")}


def test_flag_au_dessus_de_5000():
    assert est_flaggee({"montant": Decimal("5000.01")})
    assert not est_flaggee({"montant": Decimal("5000.00")})
    assert not est_flaggee({"montant": Decimal("12")})
