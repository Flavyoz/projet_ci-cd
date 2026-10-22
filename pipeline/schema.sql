-- Fichiers déjà traités : sert à ne jamais traiter deux fois le même CSV
CREATE TABLE IF NOT EXISTS fichiers_traites (
    nom_fichier TEXT PRIMARY KEY,
    traite_le   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id       TEXT PRIMARY KEY,
    datetime_transaction TIMESTAMP     NOT NULL,
    iban_origine         TEXT          NOT NULL,
    pays_source          TEXT          NOT NULL,
    banque_source        TEXT          NOT NULL,
    iban_destinataire    TEXT          NOT NULL,
    pays_destinataire    TEXT          NOT NULL,
    montant              NUMERIC(14,2) NOT NULL,
    flaggee              BOOLEAN       NOT NULL,
    nom_fichier          TEXT          NOT NULL REFERENCES fichiers_traites(nom_fichier)
);

-- Résultats des traitements (cumulés sur tous les fichiers)
CREATE TABLE IF NOT EXISTS somme_envoyee_par_iban (
    iban  TEXT PRIMARY KEY,
    total NUMERIC(16,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS somme_envoyee_par_banque (
    banque TEXT PRIMARY KEY,
    total  NUMERIC(16,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS somme_recue_par_iban (
    iban  TEXT PRIMARY KEY,
    total NUMERIC(16,2) NOT NULL
);
