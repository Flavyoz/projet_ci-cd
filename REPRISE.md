# Reprendre le projet

## Où on en est

- **Niveau 1** : code terminé. Il manque les captures d'écran de la question 6 (voir « Ce qu'il reste à faire »).
- **Niveau 2** : code terminé et testé en local. Les CSV passent par un S3 local (SeaweedFS) avant d'être traités.
- La CI n'a pas encore tourné sur GitHub, seulement en local.

## Installer et lancer (une seule fois)

Il faut **Python 3.11** et **Docker Desktop** (démarré).

```bash
python -m venv .venv
.venv\Scripts\activate              # Windows  (Mac/Linux : source .venv/bin/activate)
pip install -r requirements.txt
```

## Faire tourner la pipeline

```bash
docker compose up -d --wait               # démarre le S3 et la base PostgreSQL

python -m pipeline.main generer           # 1. crée 3 CSV dans data/
python -m pipeline.main deposer           # 2. les envoie dans le S3
python -m pipeline.main creer-tables      # 3. crée les tables
python -m pipeline.main traiter           # 4. lit le S3, calcule, écrit en base

pytest                                    # tous les tests doivent passer
```

Pour repartir de zéro (S3 et base vidés) :

```bash
docker compose down -v
```

## Qui fait quoi

| Fichier | Rôle |
|---|---|
| `pipeline/generate.py` | crée les CSV (données fixes) |
| `pipeline/s3.py` | connexion au S3, dépôt et liste des fichiers |
| `pipeline/chargement.py` | télécharge un CSV depuis le S3 et le lit |
| `pipeline/traitement.py` | calculs : sommes et flag > 5000 |
| `pipeline/schema.sql` | tables de la base |
| `pipeline/base_de_donnees.py` | écrit les résultats en base |
| `pipeline/retry.py` | réessaie en cas d'erreur + pannes simulées |
| `pipeline/main.py` | enchaîne les 4 commandes |
| `.github/workflows/ci.yml` | la CI GitHub |
| `tests/` | tests unitaires et d'intégration |
| `scenarios/` | bugs à appliquer pour les captures d'écran |

Plus de détails dans le `README.md`.

## Ce qu'il reste à faire

1. **Pousser sur GitHub** et vérifier que la CI passe au vert (onglet *Actions*).
2. **Captures d'écran de la CI** :
   - un run vert, en dépliant l'étape « Traiter les fichiers » : on y voit les retries ;
   - un run rouge par bug, avec les patchs du dossier `scenarios/`. Les commandes sont dans le `README.md`.
3. **Optionnel** : la liste « À ajouter plus tard » à la fin du `README.md` (dashboard, niveau 3…).
