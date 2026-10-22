"""Test d'intégration : à lancer APRÈS la pipeline. Vérifie les valeurs réellement insérées en base.

Les valeurs attendues sont calculées à la main à partir des données de generate.py.
"""

from decimal import Decimal as D

import pytest

from pipeline.base_de_donnees import connexion


@pytest.fixture(scope="module")
def conn():
    with connexion() as c:
        yield c


def lire(conn, sql):
    return dict(conn.execute(sql).fetchall())


def test_les_3_fichiers_sont_traites_une_seule_fois(conn):
    assert conn.execute("SELECT count(*) FROM fichiers_traites").fetchone()[0] == 3
    assert conn.execute("SELECT count(*) FROM transactions").fetchone()[0] == 18


def test_somme_envoyee_par_iban(conn):
    assert lire(conn, "SELECT iban, total FROM somme_envoyee_par_iban") == {
        "FR7630004000031234567890143": D("8619.99"),
        "FR7630004000039876543210987": D("830.00"),
        "FR1420041010050500013M02606": D("5350.51"),
        "DE89370400440532013000": D("21060.25"),
        "NL91ABNA0417164300": D("8599.99"),
        "ES9121000418450200051332": D("2545.80"),
        "GB29NWBK60161331926819": D("15875.40"),
    }


def test_somme_envoyee_par_banque(conn):
    assert lire(conn, "SELECT banque, total FROM somme_envoyee_par_banque") == {
        "BNP Paribas": D("9449.99"),
        "La Banque Postale": D("5350.51"),
        "Deutsche Bank": D("21060.25"),
        "ABN AMRO": D("8599.99"),
        "CaixaBank": D("2545.80"),
        "NatWest": D("15875.40"),
    }


def test_somme_recue_par_iban(conn):
    assert lire(conn, "SELECT iban, total FROM somme_recue_par_iban") == {
        "FR7630004000031234567890143": D("16110.75"),
        "FR1420041010050500013M02606": D("3795.40"),
        "DE89370400440532013000": D("11600.01"),
        "NL91ABNA0417164300": D("10399.99"),
        "ES9121000418450200051332": D("20600.00"),
        "GB29NWBK60161331926819": D("375.79"),
    }


def test_transactions_flaggees(conn):
    flaggees = {r[0] for r in conn.execute("SELECT transaction_id FROM transactions WHERE flaggee")}
    # T0004 = 5000.00 pile -> pas flaggée
    assert flaggees == {"T0003", "T0007", "T0009", "T0015", "T0018"}
