"""Retry (nouvel essai) et pannes simulées."""

import logging
import os
import time

log = logging.getLogger(__name__)

# Pannes simulées pour la démo : FAIL_INSERT_TIMES=2 fait échouer les 2 premières insertions.
pannes_restantes = {
    "insertion": int(os.environ.get("FAIL_INSERT_TIMES", 0)),
    "telechargement": int(os.environ.get("FAIL_DOWNLOAD_TIMES", 0)),
}


class PanneSimulee(Exception):
    pass


def simuler_panne(operation: str) -> None:
    if pannes_restantes[operation] > 0:
        pannes_restantes[operation] -= 1
        raise PanneSimulee(f"panne simulée pendant : {operation}")


def avec_retry(fonction, erreurs, tentatives=5, attente=1.0):
    """Appelle fonction(). Si elle lève une des `erreurs`, attend puis réessaie (attente x2 à chaque fois)."""
    for tentative in range(1, tentatives + 1):
        try:
            return fonction()
        except erreurs as e:
            if tentative == tentatives:
                raise
            log.warning("tentative %d/%d échouée (%s), nouvel essai dans %.0fs", tentative, tentatives, e, attente)
            time.sleep(attente)
            attente *= 2
