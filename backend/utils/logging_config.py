import logging
import logging.handlers
import os
from pathlib import Path


def setup_logging():
    """
    Configure le logging pour l'application SuccessFuel
    """
    # Créer les chemins pour les fichiers de logs
    # Utiliser le répertoire parent (racine du projet) pour le dossier logs
    project_root = Path(__file__).parent.parent.parent
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    # Chemins des fichiers de log
    general_log_path = log_dir / "general.log"
    error_log_path = log_dir / "error.log"
    security_log_path = log_dir / "security.log"

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler pour le fichier general.log
    general_handler = logging.handlers.RotatingFileHandler(
        general_log_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    general_handler.setLevel(logging.INFO)
    general_handler.setFormatter(formatter)

    # Handler pour le fichier error.log (erreurs seulement)
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Handler pour le fichier security.log (événements de sécurité)
    security_handler = logging.handlers.RotatingFileHandler(
        security_log_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(formatter)

    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(general_handler)
    root_logger.addHandler(error_handler)

    # Logger spécifique pour les événements de sécurité
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    security_logger.addHandler(security_handler)

    # Logger pour l'application
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)

    return app_logger, security_logger