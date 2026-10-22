"""Étape 1 : génère des fichiers CSV de transactions.

Les données sont écrites en dur (pas d'aléatoire) pour que les tests puissent
vérifier des valeurs exactes en base.
"""

import csv
from pathlib import Path

COLONNES = [
    "transaction_id",
    "datetime_transaction",
    "iban_origine",
    "pays_source",
    "banque_source",
    "iban_destinataire",
    "pays_destinataire",
    "montant",
]

# Comptes utilisés : lettre -> (iban, pays, banque)
COMPTES = {
    "A": ("FR7630004000031234567890143", "FR", "BNP Paribas"),
    "G": ("FR7630004000039876543210987", "FR", "BNP Paribas"),
    "B": ("FR1420041010050500013M02606", "FR", "La Banque Postale"),
    "C": ("DE89370400440532013000", "DE", "Deutsche Bank"),
    "D": ("NL91ABNA0417164300", "NL", "ABN AMRO"),
    "E": ("ES9121000418450200051332", "ES", "CaixaBank"),
    "F": ("GB29NWBK60161331926819", "GB", "NatWest"),
}

# Fichier -> liste de (id, date, compte origine, compte destinataire, montant)
FICHIERS = {
    "transactions_2026-10-01.csv": [
        ("T0001", "2026-10-01T09:15:00", "A", "C", "1200.00"),
        ("T0002", "2026-10-01T10:30:00", "B", "A", "350.50"),
        ("T0003", "2026-10-01T11:45:00", "C", "D", "7800.00"),
        ("T0004", "2026-10-01T14:00:00", "A", "E", "5000.00"),
        ("T0005", "2026-10-01T16:20:00", "D", "F", "99.99"),
        ("T0006", "2026-10-01T18:05:00", "E", "B", "2500.00"),
    ],
    "transactions_2026-10-02.csv": [
        ("T0007", "2026-10-02T08:00:00", "F", "A", "15000.00"),
        ("T0008", "2026-10-02T09:10:00", "A", "B", "420.00"),
        ("T0009", "2026-10-02T10:25:00", "B", "C", "5000.01"),
        ("T0010", "2026-10-02T12:40:00", "C", "A", "760.25"),
        ("T0011", "2026-10-02T13:55:00", "D", "E", "3100.00"),
        ("T0012", "2026-10-02T15:30:00", "E", "F", "45.80"),
        ("T0013", "2026-10-02T17:45:00", "A", "D", "1999.99"),
    ],
    "transactions_2026-10-03.csv": [
        ("T0014", "2026-10-03T07:30:00", "G", "D", "600.00"),
        ("T0015", "2026-10-03T09:00:00", "C", "E", "12500.00"),
        ("T0016", "2026-10-03T11:15:00", "F", "B", "875.40"),
        ("T0017", "2026-10-03T13:20:00", "G", "F", "230.00"),
        ("T0018", "2026-10-03T16:50:00", "D", "C", "5400.00"),
    ],
}


def generer_csv(dossier: Path) -> list[Path]:
    dossier.mkdir(parents=True, exist_ok=True)
    chemins = []
    for nom_fichier, lignes in FICHIERS.items():
        chemin = dossier / nom_fichier
        with open(chemin, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(COLONNES)
            for tx_id, date, origine, destinataire, montant in lignes:
                iban_o, pays_o, banque_o = COMPTES[origine]
                iban_d, pays_d, _ = COMPTES[destinataire]
                writer.writerow([tx_id, date, iban_o, pays_o, banque_o, iban_d, pays_d, montant])
        chemins.append(chemin)
    return chemins
