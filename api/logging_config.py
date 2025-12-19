import logging
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    Configure le système de logging pour l'application.
    """
    # Créer le répertoire de logs si nécessaire
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Formats de log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler pour les logs dans un fichier de rotation
    file_handler = RotatingFileHandler(
        f'logs/app_{datetime.now(timezone.utc).strftime("%Y%m%d")}.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Handler pour les logs d'erreurs critiques
    error_handler = RotatingFileHandler(
        f'logs/error_{datetime.now(timezone.utc).strftime("%Y%m%d")}.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Handler pour la console en développement
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Configurer le logger principal
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    # Configurer des loggers spécifiques pour les modules sensibles
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(file_handler)
    audit_logger.addHandler(error_handler)
    audit_logger.addHandler(console_handler)

    return root_logger


def get_audit_logger():
    """
    Retourne un logger spécifique pour les opérations critiques nécessitant une auditabilité.
    """
    return logging.getLogger('audit')


def log_user_action(user_id: str, action: str, details: dict = None, ip_address: str = None):
    """
    Enregistre une action utilisateur dans le journal d'audit.

    Args:
        user_id: ID de l'utilisateur qui a effectué l'action
        action: Description de l'action effectuée
        details: Détails additionnels sur l'action
        ip_address: Adresse IP de l'utilisateur (si disponible)
    """
    audit_logger = get_audit_logger()
    action_details = {
        "user_id": user_id,
        "action": action,
        "details": details,
        "ip_address": ip_address,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    audit_logger.info(f"USER_ACTION: {action_details}")


def log_transaction_error(transaction_id: str, error: Exception, context: dict = None):
    """
    Enregistre une erreur de transaction dans le journal d'audit.

    Args:
        transaction_id: ID de la transaction qui a échoué
        error: L'exception qui s'est produite
        context: Informations contextuelles sur la transaction
    """
    audit_logger = get_audit_logger()
    error_details = {
        "transaction_id": transaction_id,
        "error": str(error),
        "context": context,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    audit_logger.error(f"TRANSACTION_ERROR: {error_details}", exc_info=True)


def log_data_modification(user_id: str, model_name: str, action: str,
                        old_values: dict = None, new_values: dict = None,
                        record_id: str = None, ip_address: str = None):
    """
    Enregistre une modification de données dans le journal d'audit.

    Args:
        user_id: ID de l'utilisateur qui a effectué la modification
        model_name: Nom du modèle qui a été modifié
        action: Type d'action (create, update, delete)
        old_values: Anciennes valeurs (pour les mises à jour/suppressions)
        new_values: Nouvelles valeurs (pour les créations/mises à jour)
        record_id: ID de l'enregistrement modifié
        ip_address: Adresse IP de l'utilisateur (si disponible)
    """
    audit_logger = get_audit_logger()
    modification_details = {
        "user_id": user_id,
        "model": model_name,
        "action": action,
        "old_values": old_values,
        "new_values": new_values,
        "record_id": record_id,
        "ip_address": ip_address,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    audit_logger.info(f"DATA_MODIFICATION: {modification_details}")


def log_security_event(event_type: str, details: dict, severity: str = "INFO"):
    """
    Enregistre un événement de sécurité dans le journal.

    Args:
        event_type: Type de l'événement de sécurité
        details: Détails de l'événement
        severity: Niveau de gravité (INFO, WARNING, ERROR, CRITICAL)
    """
    audit_logger = get_audit_logger()
    event_details = {
        "event_type": event_type,
        "details": details,
        "severity": severity,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    if severity == "CRITICAL":
        audit_logger.critical(f"SECURITY_EVENT: {event_details}")
    elif severity == "ERROR":
        audit_logger.error(f"SECURITY_EVENT: {event_details}")
    elif severity == "WARNING":
        audit_logger.warning(f"SECURITY_EVENT: {event_details}")
    else:
        audit_logger.info(f"SECURITY_EVENT: {event_details}")