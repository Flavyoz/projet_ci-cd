# Pipeline data – intégration continue

```
generer (CSV) ──► deposer (S3 local) ──► traiter : télécharger ─► calculer ─► insérer ──► PostgreSQL
                                                    (retry)                    (retry)
```

## Lancer en local

```bash
pip install -r requirements.txt
docker compose up -d --wait               # démarre le S3 (SeaweedFS) et PostgreSQL

python -m pipeline.main generer           # crée 3 CSV dans data/
python -m pipeline.main deposer           # les envoie dans le S3
python -m pipeline.main creer-tables      # crée les tables
python -m pipeline.main traiter           # S3 -> calculs -> base

pytest                                    # tests unitaires + test d'intégration
```

## Les fichiers

| Fichier | Rôle | Question du sujet |
|---|---|---|
| [pipeline/generate.py](pipeline/generate.py) | Écrit 3 CSV aux données fixes (6, 7 et 5 transactions) | N1.1 |
| [pipeline/chargement.py](pipeline/chargement.py) | Télécharge un CSV depuis le S3 et le lit | N1.2, N2.3 |
| [pipeline/traitement.py](pipeline/traitement.py) | Sommes et flag > 5000 (fonctions pures) | N1.2 |
| [pipeline/schema.sql](pipeline/schema.sql) | Tables de la base | N1.3 |
| [pipeline/base_de_donnees.py](pipeline/base_de_donnees.py) | Insertion des résultats | N1.3 |
| [pipeline/s3.py](pipeline/s3.py) | Connexion au S3, dépôt et liste des fichiers | N2.1, N2.2 |
| [pipeline/retry.py](pipeline/retry.py) | Nouvel essai en cas d'erreur + pannes simulées | N1.7, N2.4 |
| [pipeline/main.py](pipeline/main.py) | Enchaîne les étapes | – |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | La pipeline CI | N1.4 |
| [tests/test_integration.py](tests/test_integration.py) | Vérifie les valeurs en base | N1.5 |
| [scenarios/](scenarios/) | Bugs à injecter pour les captures | N1.6 |

En plus des colonnes demandées, le CSV contient `transaction_id` et `montant` (le montant est nécessaire pour les sommes).

## Ne jamais traiter deux fois un fichier

- La table `fichiers_traites` garde le nom de chaque fichier déjà traité. `traiter` ignore ces fichiers.
- L'insertion d'un fichier se fait dans **une seule transaction SQL** : en cas d'erreur, rien n'est enregistré.
  Le retry repart donc de zéro, sans risque de compter deux fois.

## Scénarios d'échec (captures, question 6)

```bash
git switch -c demo/bug-generation
git apply scenarios/01-bug-generation.patch   # montants écrits "1200,00" au lieu de "1200.00"
git commit -am "bug de génération" && git push -u origin demo/bug-generation
```
→ l'étape « Traiter les fichiers » échoue (`decimal.InvalidOperation`).

```bash
git switch main && git switch -c demo/bug-traitement
git apply scenarios/02-bug-traitement.patch   # >= au lieu de > : 5000 € pile est flaggé
git commit -am "bug de traitement" && git push -u origin demo/bug-traitement
```
→ le job « tests-unitaires » échoue (`test_flag_au_dessus_de_5000`).

## Bug d'insertion et retry (question 7)

La CI lance `traiter` avec `FAIL_INSERT_TIMES=2` et `FAIL_DOWNLOAD_TIMES=1`. Les logs montrent les échecs
puis la réussite :

```
WARNING tentative 1/5 échouée (panne simulée pendant : insertion), nouvel essai dans 1s
WARNING tentative 2/5 échouée (panne simulée pendant : insertion), nouvel essai dans 2s
INFO transactions_2026-10-01.csv : traité (6 transactions)
```

Avec `FAIL_INSERT_TIMES=10`, les 5 essais échouent et la pipeline devient rouge. Le fichier n'est pas marqué
comme traité, il sera donc traité au prochain lancement.

## À ajouter plus tard (hors du strict minimum)

- **Niveau 3** : CD qui déploie S3 + base + traitement via Docker sur une VM, avec lancement régulier du traitement.
- **Niveau 3** : OCR sur des images, SLM sur du texte brut, Terraform/OpenTofu.
- Dashboard (Grafana ou Metabase) branché sur la base (cité dans l'intro du sujet).
- Détection d'un même contenu déposé sous un autre nom (checksum).
- Validation plus stricte des CSV (codes pays, montants négatifs, doublons).
- Lint (ruff) dans la CI.
