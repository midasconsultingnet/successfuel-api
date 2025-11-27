import sys
import os
# Ajouter le dossier backend au chemin Python
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

# Maintenant importer le module de configuration
from utils.logging_config import setup_logging

# Initialiser la configuration de logging
app_logger, security_logger = setup_logging()

def test_logging():
    # Test des logs généraux
    app_logger.info("Ceci est un message d'information de test")
    app_logger.warning("Ceci est un message d'avertissement de test")
    app_logger.error("Ceci est un message d'erreur de test")

    # Test des logs de sécurité
    security_logger.info("Ceci est un message d'événement de sécurité de test")

    # Test des logs d'erreur
    try:
        1 / 0
    except ZeroDivisionError:
        app_logger.exception("Erreur de division par zéro détectée")

if __name__ == "__main__":
    test_logging()
    print("Test de logging terminé. Vérifiez les fichiers dans le dossier 'logs'.")